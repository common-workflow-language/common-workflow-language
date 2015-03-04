import avro.schema
import json
import pprint
import copy
from flatten import flatten
import functools
import os
from pathmapper import PathMapper, DockerPathMapper
import sandboxjs
from job import Job
import yaml
import glob
import logging

TOOL_CONTEXT_URL = "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-2-pa/schemas/draft-2/context.json"

module_dir = os.path.dirname(os.path.abspath(__file__))

class ValidationException(Exception):
    pass

def validate(expected_schema, datum):
    try:
        return validate_ex(expected_schema, datum)
    except ValidationException:
        return False

INT_MIN_VALUE = -(1 << 31)
INT_MAX_VALUE = (1 << 31) - 1
LONG_MIN_VALUE = -(1 << 63)
LONG_MAX_VALUE = (1 << 63) - 1

def validate_ex(expected_schema, datum):
    """Determine if a python datum is an instance of a schema."""
    schema_type = expected_schema.type
    if schema_type == 'null':
        if datum is None:
            return True
        else:
            raise ValidationException("`%s` is not null" % datum)
    elif schema_type == 'boolean':
        if isinstance(datum, bool):
            return True
        else:
            raise ValidationException("`%s` is not boolean" % datum)
    elif schema_type == 'string':
        if isinstance(datum, basestring):
            return True
        else:
            raise ValidationException("`%s` is not string" % datum)
    elif schema_type == 'bytes':
        if isinstance(datum, str):
            return True
        else:
            raise ValidationException("`%s` is not bytes" % datum)
    elif schema_type == 'int':
        if ((isinstance(datum, int) or isinstance(datum, long))
            and INT_MIN_VALUE <= datum <= INT_MAX_VALUE):
            return True
        else:
            raise ValidationException("`%s` is not int" % datum)
    elif schema_type == 'long':
        if ((isinstance(datum, int) or isinstance(datum, long))
            and LONG_MIN_VALUE <= datum <= LONG_MAX_VALUE):
            return True
        else:
            raise ValidationException("`%s` is not long" % datum)
    elif schema_type in ['float', 'double']:
        if (isinstance(datum, int) or isinstance(datum, long)
            or isinstance(datum, float)):
            return True
        else:
            raise ValidationException("`%s` is not float or double" % datum)
    elif schema_type == 'fixed':
        if isinstance(datum, str) and len(datum) == expected_schema.size:
            return True
        else:
            raise ValidationException("`%s` is not fixed" % datum)
    elif schema_type == 'enum':
        if datum in expected_schema.symbols:
            return True
        else:
            raise ValidationException("`%s`\n is not a valid enum symbol, expected\n %s" % (pprint.pformat(datum), pprint.pformat(expected_schema.symbols)))
    elif schema_type == 'array':
        if isinstance(datum, list):
            for i, d in enumerate(datum):
                try:
                    validate_ex(expected_schema.items, d)
                except ValidationException as v:
                    raise ValidationException("%s\n while validating item at position %i `%s`" % (v, i, d))
            return True
        else:
            raise ValidationException("`%s`\n is not a list, expected list of\n %s" % (pprint.pformat(datum), expected_schema.items))
    elif schema_type == 'map':
        if (isinstance(datum, dict) and
            False not in [isinstance(k, basestring) for k in datum.keys()] and
            False not in [validate(expected_schema.values, v) for v in datum.values()]):
            return True
        else:
            raise ValidationException("`%s` is not a valid map value, expected\n %s" % (pprint.pformat(datum), pprint.pformat(expected_schema.values)))
    elif schema_type in ['union', 'error_union']:
        if True in [validate(s, datum) for s in expected_schema.schemas]:
            return True
        else:
            errors = []
            for s in expected_schema.schemas:
                try:
                    validate_ex(s, datum)
                except ValidationException as e:
                    errors.append(str(e))
            raise ValidationException("`%s`\n is not valid, expected one of:\n\n%s\n\n the individual errors are:\n%s" % (pprint.pformat(datum), ",\n\n  ".join([str(s) for s in expected_schema.schemas]), ";\n\n".join(errors)))
    elif schema_type in ['record', 'error', 'request']:
        if not isinstance(datum, dict):
            raise ValidationException("`%s`\n is not a dict" % pprint.pformat(datum))
        try:
            for f in expected_schema.fields:
                validate_ex(f.type, datum.get(f.name))
            return True
        except ValidationException as v:
            raise ValidationException("%s\n while validating field `%s`" % (v, f.name))
    raise ValidationException("Unrecognized schema_type %s" % schema_type)

class Builder(object):
    def jseval(self, expression, context):
        if isinstance(expression, list):
            exp = "{return %s(%s);}" % (expression[0], ",".join([json.dumps(self.do_eval(e)) for e in expression[1:]]))
        elif expression.startswith('{'):
            exp = '{return function()%s();}' % (expression)
        else:
            exp = '{return %s;}' % (expression)
        return sandboxjs.execjs(exp, "var $job = %s; var $self = %s; %s" % (json.dumps(self.job), json.dumps(context), self.jslib))

    def do_eval(self, ex, context=None):
        if isinstance(ex, dict):
            if ex.get("expressionType") == "javascript":
                return self.jseval(ex["value"], context)
            elif ex.get("ref"):
                with open(os.path.join(self.basedir, ex["ref"]), "r") as f:
                    return f.read()
        else:
            return ex

    def bind_input(self, schema, datum):
        bindings = []

        # Handle union types
        if isinstance(schema["type"], list):
            success = False
            for t in schema["type"]:
                if t in self.schemaDefs:
                    t = self.schemaDefs[t]
                avsc = avro.schema.make_avsc_object(t, None)
                if validate(avsc, datum):
                    if isinstance(t, basestring):
                        t = {"type": t}
                    bindings.extend(self.bind_input(t, datum))
                    success = True
                    break
            if not success:
                raise ValidationException("'%s' is not a valid union %s" % (datum, schema["type"]))
        elif isinstance(schema["type"], dict):
            bindings.extend(self.bind_input(schema["type"], datum))
        else:
            if schema["type"] in self.schemaDefs:
                schema = self.schemaDefs[schema["type"]]

            if schema["type"] == "record":
                for f in schema["fields"]:
                    if f["name"] in datum:
                        b = self.bind_input(f, datum[f["name"]])
                        for bi in b:
                            bi["position"].append(f["name"])
                        bindings.extend(b)

            if schema["type"] == "map":
                for v in datum:
                    b = self.bind_input(schema["values"], datum[v])
                    for bi in b:
                        bi["position"].insert(0, v)
                    bindings.extend(b)

            if schema["type"] == "array":
                for n, item in enumerate(datum):
                    b = self.bind_input({"type": schema["items"], "binding": schema.get("binding")}, item)
                    for bi in b:
                        bi["position"].insert(0, n)
                    bindings.extend(b)

            if schema["type"] == "File":
                self.files.append(datum["path"])

        b = None
        if "binding" in schema and isinstance(schema["binding"], dict):
            b = copy.copy(schema["binding"])

            if b.get("position"):
                b["position"] = [b["position"]]
            else:
                b["position"] = [0]

            # Position to front of the sort key
            for bi in bindings:
                bi["position"] = b["position"] + bi["position"]

            if "valueFrom" in b:
                b["valueFrom"] = self.do_eval(b["valueFrom"], datum)
            else:
                b["valueFrom"] = datum

            if schema["type"] == "File":
                b["is_file"] = True
            bindings.append(b)

        return bindings

    def generate_arg(self, binding):
        value = binding["valueFrom"]
        prefix = binding.get("prefix")
        sep = binding.get("separator")

        l = []
        if isinstance(value, list):
            if binding.get("itemSeparator"):
                l = [binding["itemSeparator"].join([str(v) for v in value])]
            elif prefix:
                return [prefix]
        elif binding.get("is_file"):
            l = [self.pathmapper.mapper(value["path"])]
        elif isinstance(value, dict):
            if prefix:
                return [prefix]
        elif isinstance(value, bool):
            if value and prefix:
                return [prefix]
            else:
                return []
        else:
            l = [value]

        args = []
        for j in l:
            if sep is None or sep == " ":
                args.extend([prefix, str(j)])
            else:
                args.extend([prefix + sep + str(j)])

        return [a for a in args if a is not None]

class Tool(object):
    def __init__(self, toolpath_object):
        self.names = avro.schema.Names()
        cwl_avsc = os.path.join(module_dir, 'schemas/draft-2/cwl.avsc')
        with open(cwl_avsc) as f:
            j = json.load(f)
            for t in j:
                avro.schema.make_avsc_object(t, self.names)

        self.tool = toolpath_object
        if self.tool.get("@context") != TOOL_CONTEXT_URL:
            raise Exception("Missing or invalid '@context' field in tool description document, must be %s" % TOOL_CONTEXT_URL)

        # Validate tool documument
        validate_ex(self.names.get_name("CommandLineTool", ""), self.tool)

        # Import schema defs
        self.schemaDefs = {}
        if self.tool.get("schemaDefs"):
            for i in self.tool["schemaDefs"]:
                avro.schema.make_avsc_object(i, self.names)
                self.schemaDefs[i["name"]] = i

        # Build record schema from inputs
        self.inputs_record_schema = {"name": "input_record_schema", "type": "record", "fields": []}
        for i in self.tool["inputs"]:
            c = copy.copy(i)
            c["name"] = c["port"][1:]
            del c["port"]
            self.inputs_record_schema["fields"].append(c)
        avro.schema.make_avsc_object(self.inputs_record_schema, self.names)

        self.outputs_record_schema = {"name": "outputs_record_schema", "type": "record", "fields": []}
        for i in self.tool["outputs"]:
            c = copy.copy(i)
            c["name"] = c["port"][1:]
            del c["port"]
            self.outputs_record_schema["fields"].append(c)
        avro.schema.make_avsc_object(self.outputs_record_schema, self.names)

    def job(self, joborder, basedir, use_container=True):
        # Validate job order
        validate_ex(self.names.get_name("input_record_schema", ""), joborder)

        builder = Builder()
        builder.job = joborder
        builder.jslib = ''
        builder.basedir = basedir
        builder.files = []
        builder.bindings = []
        builder.schemaDefs = self.schemaDefs

        if isinstance(self.tool["baseCommand"], list):
            for n, b in enumerate(self.tool["baseCommand"]):
                builder.bindings.append({
                    "position": [-1000000, n],
                    "valueFrom": b
                })
        else:
            builder.bindings.append({
                "position": [-1000000],
                "valueFrom": self.tool["baseCommand"]
            })

        if self.tool.get("expressionDefs"):
            for ex in self.tool['expressionDefs']:
                builder.jslib += builder.do_eval(ex) + "\n"

        if self.tool.get("arguments"):
            for i, a in enumerate(self.tool["arguments"]):
                a = copy.copy(a)
                if a.get("position"):
                    a["position"] = [a["position"], i]
                else:
                    a["position"] = [0, i]
                a["valueFrom"] = builder.do_eval(a["valueFrom"])
                builder.bindings.append(a)

        builder.bindings.extend(builder.bind_input(self.inputs_record_schema, joborder))
        builder.bindings.sort(key=lambda a: a["position"])

        logging.debug(pprint.pformat(builder.bindings))
        logging.debug(pprint.pformat(builder.files))

        j = Job()
        j.joborder = joborder
        j.container = None
        builder.pathmapper = None

        if self.tool.get("stdin"):
            j.stdin = builder.do_eval(self.tool["stdin"])
            builder.files.append(j.stdin)
        else:
            j.stdin = None

        if self.tool.get("stdout"):
            j.stdout = builder.do_eval(self.tool["stdout"])
            if os.path.isabs(j.stdout):
                raise Exception("stdout must be a relative path")
        else:
            j.stdout = None

        j.generatefiles = {}
        for t in self.tool.get("fileDefs", []):
            j.generatefiles[t["filename"]] = builder.do_eval(t["value"])

        for r in self.tool.get("hints", []):
            if r["requirementType"] == "DockerImage" and use_container:
                j.container = {}
                j.container["type"] = "docker"
                if "dockerPull" in r:
                    j.container["pull"] = r["dockerPull"]
                if "dockerImport" in r:
                    j.container["import"] = r["dockerImport"]
                if "dockerImageId" in r:
                    j.container["imageId"] = r["dockerImageId"]
                else:
                    j.container["imageId"] = r["dockerPull"]
                builder.pathmapper = DockerPathMapper(builder.files, basedir)

        if builder.pathmapper is None:
            builder.pathmapper = PathMapper(builder.files, basedir)
        j.command_line = flatten(map(builder.generate_arg, builder.bindings))

        if j.stdin:
            j.stdin = j.stdin if os.path.isabs(j.stdin) else os.path.join(basedir, j.stdin)

        j.pathmapper = builder.pathmapper
        j.collect_outputs = functools.partial(self.collect_output_ports, self.tool["outputs"], builder)

        return j

    def collect_output_ports(self, ports, builder, outdir):
        custom_output = os.path.join(outdir, "output.cwl.json")
        if os.path.exists(custom_output):
            outputdoc = yaml.load(custom_output)
            validate_ex(self.names.get_name("output_record_schema", ""), outputdoc)
            return outputdoc
        return {port["port"][1:]: self.collect_output(port, builder, outdir) for port in ports}

    def collect_output(self, schema, builder, outdir):
        r = None
        if "binding" in schema:
            binding = schema["binding"]
            if ("glob" in binding and
                (schema["type"] == "File" or
                 (schema["type"] == "array" and
                  schema["items"] == "File"))):
                r = [{"path": g} for g in glob.glob(os.path.join(outdir, binding["glob"]))]
                if schema["type"] == "File":
                    r = r[0] if r else None
            elif "valueFrom" in binding:
                r = builder.do_eval(binding["valueFrom"])

        if not r and schema["type"] == "record":
            r = {}
            for f in schema["fields"]:
                r[f["name"]] = self.collect_output(f, builder, outdir)

        return r
