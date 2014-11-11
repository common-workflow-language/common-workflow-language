import os
import pprint
import json
import execjs
import copy
import sys
import jsonschema.exceptions

from jsonschema.validators import Draft4Validator
from ref_resolver import from_url, resolve_pointer

module_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(module_dir, 'schemas/tool.json')) as f:
    tool_schema_doc = json.load(f)
with open(os.path.join(module_dir, 'schemas/metaschema.json')) as f:
    metaschema = json.load(f)

def fix_metaschema(m):
    if isinstance(m, dict):
        if '$ref' in m and m['$ref'].startswith("metaschema.json"):
            m['$ref'] = "file:%s/schemas/%s" % (module_dir, m['$ref'])
        else:
            for k in m:
                fix_metaschema(m[k])
    if isinstance(m, list):
        for k in m:
            fix_metaschema(k)

fix_metaschema(tool_schema_doc)

tool_schema = Draft4Validator(tool_schema_doc)

class Job(object):
    def run(self):
        pass

def each(l):
    if l is None:
        return []
    if isinstance(l, (list, tuple)):
        return l
    else:
        return [l]

# http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
def flatten(l, ltypes=(list, tuple)):
    if l is None:
        return []
    if not isinstance(l, ltypes):
        return [l]

    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def fix_file_type(t):
    if 'type' in t and t['type'] == "file":
        for a in metaschema["definitions"]["file"]:
            t[a] = metaschema["definitions"]["file"][a]
        t["_type"] = "file"
    for k in t:
        if isinstance(t[k], dict):
            fix_file_type(t[k])

def jseval(job=None, expression=None):
    if expression.startswith('{'):
        exp_tpl = '''function () {
        $job = %s;
        return function()%s();}()
        '''
    else:
        exp_tpl = '''function () {
        $job = %s;
        return %s;}()
        '''
    exp = exp_tpl % (json.dumps(job), expression)
    return execjs.eval(exp)

def adapt_inputs(schema, inp, key):
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
                a = adapt_inputs(schema["properties"][i], inp[i], i)
                adapters.extend(a)
    elif isinstance(inp, list):
        for n, i in enumerate(inp):
            a = adapt_inputs(schema["items"], i, format(n, '06'))
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

def to_str(schema, value):
    if "$ref" in schema:
        schema = from_url(schema["$ref"])

    if 'oneOf' in schema:
        for a in schema['oneOf']:
            v = to_str(a, value)
            if v is not None:
                return v
        return None
    elif 'type' in schema:
        if schema["type"] == "array" and isinstance(value, list):
            return [to_str(schema["items"], v) for v in value]
        elif schema["type"] == "object" and isinstance(value, dict):
            if "path" in value:
                return value["path"]
            else:
                raise Exception("Not expecting a dict %s" % (value))
        elif schema["type"] in ("string", "number", "integer"):
            return str(value)
        elif schema["type"] == "boolean":
            # need special handling for flags
            return str(value)

    return None

def adapt(adapter, job):
    if "value" in adapter:
        value = adapter["value"]
        if isinstance(value, dict):
            if "$expr" in value:
                value = jseval(job, value["$expr"]["value"])
            elif "$job" in value:
                value = resolve_pointer(job, value["$job"])

    value = to_str(adapter["schema"], value)

    sep = adapter["separator"] if "separator" in adapter else ''

    if 'itemSeparator' in adapter:
        if adapter["prefix"]:
            l = [adapter["prefix"] + adapter['itemSeparator'].join(value)]
        else:
            l = [adapter['itemSeparator'].join(value)]
    elif 'prefix' in adapter:
        l = []
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
        tool_schema.validate(self.tool)


    def job(self, joborder):
        inputs = joborder['inputs']
        Draft4Validator(self.tool['inputs']).validate(inputs)

        adapter = self.tool["adapter"]
        adapters = [{"order": [-1000000],
                     "schema": tool_schema_doc["properties"]["adapter"]["properties"]["baseCmd"],
                     "value": adapter['baseCmd'],
                     #"_key": "0"
                 }]

        if "args" in adapter:
            for i, a in enumerate(adapter["args"]):
                a = copy.copy(a)
                if "order" in a:
                    a["order"] = [a["order"]]
                else:
                    a["order"] = [0]
                a["schema"] = tool_schema_doc["definitions"]["strOrExpr"]
                #a["_key"] = "!" + format(i, '06')
                adapters.append(a)

        adapters.extend(adapt_inputs(self.tool['inputs'], inputs, ""))

        adapters.sort(key=lambda a: a["order"])

        j = Job()
        j.command_line = flatten(map(lambda adapter: adapt(adapter, joborder), adapters))

        if 'stdin' in adapter:
            j.stdin = flatten(adapt({"value": adapter['stdin'],
                                     "schema": tool_schema_doc["properties"]["adapter"]["properties"]["stdin"]
                                 }, joborder))[0]
        else:
            j.stdin = None

        if 'stdout' in adapter:
            j.stdout = flatten(adapt({"value": adapter['stdout'],
                                      "schema": tool_schema_doc["properties"]["adapter"]["properties"]["stdout"]}, joborder))[0]
        else:
            j.stdout = None

        return j
