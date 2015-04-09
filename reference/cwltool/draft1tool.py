import os
import pprint
import json
import sandboxjs
import copy
import sys
import jsonschema.exceptions
import random
import requests
import urlparse
import functools
from pathmapper import PathMapper, DockerPathMapper
from job import CommandLineJob
from flatten import flatten

from jsonschema.validators import Draft4Validator
import ref_resolver
from ref_resolver import from_url, resolve_pointer

module_dir = os.path.dirname(os.path.abspath(__file__))

jsonschemapath = os.path.join(module_dir, 'schemas/draft-1/json-schema-draft-04.json')
with open(jsonschemapath) as f:
    jsonschemapath_doc = json.load(f)

ref_resolver.loader.fetched["http://json-schema.org/draft-04/schema"] = jsonschemapath_doc

toolpath = os.path.join(module_dir, 'schemas/draft-1/tool.json')
with open(toolpath) as f:
    tool_schema_doc = json.load(f)
with open(os.path.join(module_dir, 'schemas/draft-1/metaschema.json')) as f:
    metaschema = json.load(f)

SCHEMA_URL_PREFIX = "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/"
TOOL_SCHEMA_URL = SCHEMA_URL_PREFIX + "tool.json"
METASCHEMA_SCHEMA_URL = SCHEMA_URL_PREFIX + "metaschema.json"

ref_resolver.loader.fetched[TOOL_SCHEMA_URL] = tool_schema_doc
ref_resolver.loader.fetched[METASCHEMA_SCHEMA_URL] = metaschema

tool_schema = Draft4Validator(tool_schema_doc)

def each(l):
    if l is None:
        return []
    if isinstance(l, (list, tuple)):
        return l
    else:
        return [l]

def fix_file_type(t):
    if 'type' in t and t['type'] == "file":
        for a in metaschema["definitions"]["file"]:
            t[a] = metaschema["definitions"]["file"][a]
        t["_type"] = "file"
    for k in t:
        if isinstance(t[k], dict):
            fix_file_type(t[k])

class Builder(object):

    def jseval(self, job=None, expression=None):
        if expression.startswith('{'):
            exp_tpl = '''{
            return function()%s();}
            '''
        else:
            exp_tpl = '''{
            return %s;}
            '''
        exp = exp_tpl % (expression)
        return sandboxjs.execjs(exp, "var $job = %s;%s" % (json.dumps(job), self.jslib))

    def resolve_eval(self, job, v):
        if isinstance(v, dict):
            if "$expr" in v:
                # Support $import of the $expr
                return self.jseval(job, self.resolve_eval(job, v["$expr"]))
            if "$apply" in v:
                # Support $import of the $expr
                ex = ""
                for i, p in enumerate(v["$apply"]):
                    if i == 0:
                        ex += p + "("
                    else:
                        ex += json.dumps(self.resolve_eval(job, p))
                        if i < len(v["$apply"])-1:
                            ex += ","
                ex += ")"
                return self.jseval(job, ex)
            elif "$job" in v:
                return resolve_pointer(job, v["$job"])
            elif "$import" in v:
                # TODO: check checksum
                url = urlparse.urljoin(self.base_url, v["$import"])
                split = urlparse.urlsplit(url)
                scheme, path = split.scheme, split.path
                if scheme in ['http', 'https']:
                    resp = requests.get(url)
                    try:
                        resp.raise_for_status()
                    except Exception as e:
                        raise RuntimeError(url, e)
                    return resp.text
                elif scheme == 'file':
                    try:
                        with open(path) as fp:
                            return fp.read()
                    except (OSError, IOError) as e:
                        raise RuntimeError('Failed for %s: %s' % (url, e))
                else:
                    raise ValueError('Unsupported scheme: %s' % scheme)
        return v

    def adapt_inputs(self, schema, job, inp, key):
        adapters = []

        if 'oneOf' in schema:
            for one in schema["oneOf"]:
                try:
                    Draft4Validator(one).validate(inp)
                    schema = one
                    break
                except jsonschema.exceptions.ValidationError:
                    pass

        if isinstance(inp, dict):
            if "properties" in schema:
                for i in inp:
                    a = self.adapt_inputs(schema["properties"][i], job, inp[i], i)
                    adapters.extend(a)
        elif isinstance(inp, list):
            for n, i in enumerate(inp):
                a = self.adapt_inputs(schema["items"], job, i, format(n, '06'))
                for x in a:
                    x["order"].insert(0, n)
                adapters.extend(a)

        if 'adapter' in schema:
            a = copy.copy(schema['adapter'])

            if "order" in a:
                a["order"] = [a["order"], key]
            else:
                a["order"] = [1000000, key]

            a["schema"] = schema

            for x in adapters:
                x["order"] = a["order"] + x["order"]

            if not 'value' in a and len(adapters) == 0:
                a['value'] = inp

            if len(adapters) == 0 or "value" in a:
                adapters.insert(0, a)

        return adapters

    def to_str(self, schema, value, path_mapper):
        if "$ref" in schema:
            schema = from_url(schema["$ref"], self.ref_base_url)

        if 'oneOf' in schema:
            for a in schema['oneOf']:
                v = self.to_str(a, value, path_mapper)
                if v is not None:
                    return v
            return None
        elif 'type' in schema:
            if schema["type"] == "array" and isinstance(value, list):
                return [self.to_str(schema["items"], v, path_mapper) for v in value]
            elif schema["type"] == "object" and isinstance(value, dict):
                if "path" in value:
                    return path_mapper(value["path"])
                else:
                    raise Exception("Not expecting a dict %s" % (value))
            elif schema["type"] in ("string", "number", "integer"):
                return str(value)
            elif schema["type"] == "boolean":
                # handled specially by adapt()
                return value

        return None

    def find_files(self, adapter, job):
        if "value" in adapter:
            value = self.resolve_eval(job, adapter["value"])
        else:
            return None

        schema = adapter["schema"]

        if "$ref" in schema:
            schema = from_url(schema["$ref"], self.ref_base_url)

        if 'oneOf' in schema:
            for a in schema['oneOf']:
                v = self.find_files(a, value)
                if v is not None:
                    return v
            return None
        elif 'type' in schema:
            if schema["type"] == "array" and isinstance(value, list):
                return [self.find_files({"value": v,
                                    "schema": schema["items"]}, job) for v in value]
            elif schema["type"] == "object" and isinstance(value, dict):
                if "path" in value:
                    return value["path"]
                else:
                    raise Exception("Not expecting a dict %s" % (value))

        return None


    def adapt(self, adapter, job, path_mapper):
        if "value" in adapter:
            value = self.resolve_eval(job, adapter["value"])
        else:
            raise Exception("No value in adapter")

        value = self.to_str(adapter["schema"], value, path_mapper)

        sep = adapter["separator"] if "separator" in adapter else " "

        if 'itemSeparator' in adapter:
            if adapter["prefix"]:
                l = [adapter["prefix"] + adapter['itemSeparator'].join(value)]
            else:
                l = [adapter['itemSeparator'].join(value)]
        elif 'prefix' in adapter:
            l = []
            if value is True:
                l.append(adapter["prefix"])
            elif value is False:
                pass
            else:
                for v in each(value):
                    if sep == " ":
                        l.append(adapter["prefix"])
                        l.append(v)
                    else:
                        l.append(adapter["prefix"] + sep + v)
        else:
            l = [value]

        return l

class Tool(object):
    def __init__(self, toolpath_object):
        self.tool = toolpath_object
        fix_file_type(self.tool)
        if "schema" not in self.tool or self.tool["schema"] != TOOL_SCHEMA_URL:
            raise Exception("Missing or invalid 'schema' field in tool description document, must be %s" % TOOL_SCHEMA_URL)
        tool_schema.validate(self.tool)

    def job(self, joborder, basedir, output_callback, use_container=True):
        inputs = joborder['inputs']
        Draft4Validator(self.tool['inputs']).validate(inputs)

        adapter = self.tool["adapter"]
        adapters = [{"order": [-1000000],
                     "schema": tool_schema_doc["properties"]["adapter"]["properties"]["baseCmd"],
                     "value": adapter['baseCmd']
                 }]

        builder = Builder()
        builder.base_url = "file:"+os.path.abspath(basedir)+"/"
        builder.ref_base_url = "file:"+toolpath

        requirements = self.tool.get("requirements")
        builder.jslib = ''
        if requirements and 'expressionlib' in requirements:
            for ex in requirements['expressionlib']:
                builder.jslib += builder.resolve_eval(joborder, ex) + "\n"

        if "args" in adapter:
            for i, a in enumerate(adapter["args"]):
                a = copy.copy(a)
                if "order" in a:
                    a["order"] = [a["order"]]
                else:
                    a["order"] = [0]
                a["schema"] = tool_schema_doc["definitions"]["strOrExpr"]
                adapters.append(a)

        adapters.extend(builder.adapt_inputs(self.tool['inputs'], inputs, inputs, ""))

        adapters.sort(key=lambda a: a["order"])

        referenced_files = filter(lambda a: a is not None, flatten(map(lambda a: builder.find_files(a, joborder), adapters)))

        j = CommandLineProcess()
        j.joborder = joborder
        j.container = None

        if 'stdin' in adapter:
            j.stdin = flatten(builder.adapt({"value": adapter['stdin'],
                                              "schema": tool_schema_doc["properties"]["adapter"]["properties"]["stdin"]
                                          }, joborder, None))[0]
            referenced_files.append(j.stdin)
        else:
            j.stdin = None

        if 'stdout' in adapter:
            j.stdout = flatten(builder.adapt({"value": adapter['stdout'],
                                               "schema": tool_schema_doc["properties"]["adapter"]["properties"]["stdout"]
                                           }, joborder, None))[0]

            if os.path.isabs(j.stdout):
                raise Exception("stdout must be a relative path")
        else:
            j.stdout = None

        j.generatefiles = {}
        for t in adapter.get("generatefiles", []):
            j.generatefiles[builder.resolve_eval(inputs, t["name"])] = builder.resolve_eval(inputs, t["value"])

        d = None
        if requirements:
            b = requirements.get("environment")
            if b:
                c = b.get("container")
                if use_container and c:
                    if c.get("type") == "docker":
                        d = DockerPathMapper(referenced_files, basedir)
                        j.container = c

        if d is None:
            d = PathMapper(referenced_files, basedir)

        if j.stdin:
            j.stdin = j.stdin if os.path.isabs(j.stdin) else os.path.join(basedir, j.stdin)

        j.command_line = flatten(map(lambda a: builder.adapt(a, joborder, d.mapper), adapters))

        j.pathmapper = d
        j.collect_outputs = functools.partial(self.collect_outputs, self.tool.get("outputs", {}), joborder)
        j.output_callback = output_callback

        yield j

    def collect_outputs(self, schema, joborder, outdir):
        result_path = os.path.join(outdir, "result.cwl.json")
        if os.path.isfile(result_path):
            print "Result file found."
            with open(result_path) as fp:
                return yaml.load(fp)

        r = None
        if isinstance(schema, dict):
            if "adapter" in schema:
                adapter = schema["adapter"]
                if "glob" in adapter:
                    r = [{"path": g} for g in glob.glob(os.path.join(outdir, adapter["glob"]))]
                    if not ("type" in schema and schema["type"] == "array"):
                        if r:
                            r = r[0]
                        else:
                            r = None
                if "value" in adapter:
                    r = draft1tool.resolve_eval(joborder, adapter["value"])
            if not r and "properties" in schema:
                r = {}
                for k, v in schema["properties"].items():
                    out = self.collect_outputs(v, joborder, outdir)
                    if out:
                        r[k] = out

        return r
