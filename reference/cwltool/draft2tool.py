import avro.schema
import json
import pprint
import copy
from flatten import flatten
import os
from pathmapper import PathMapper, DockerPathMapper
import sandboxjs

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
        raise ValidationException("'%s' is not None" % datum)
  elif schema_type == 'boolean':
    if isinstance(datum, bool):
        return True
    else:
        raise ValidationException("'%s' is not bool" % datum)
  elif schema_type == 'string':
    if isinstance(datum, basestring):
        return True
    else:
        raise ValidationException("'%s' is not string" % datum)
  elif schema_type == 'bytes':
    if isinstance(datum, str):
        return True
    else:
        raise ValidationException("'%s' is not bytes" % datum)
  elif schema_type == 'int':
    if ((isinstance(datum, int) or isinstance(datum, long))
            and INT_MIN_VALUE <= datum <= INT_MAX_VALUE):
        return True
    else:
        raise ValidationException("'%s' is not int" % datum)
  elif schema_type == 'long':
    if ((isinstance(datum, int) or isinstance(datum, long))
            and LONG_MIN_VALUE <= datum <= LONG_MAX_VALUE):
        return True
    else:
        raise ValidationException("'%s' is not long" % datum)
  elif schema_type in ['float', 'double']:
    if (isinstance(datum, int) or isinstance(datum, long)
            or isinstance(datum, float)):
        return True
    else:
        raise ValidationException("'%s' is not float or double" % datum)
  elif schema_type == 'fixed':
    if isinstance(datum, str) and len(datum) == expected_schema.size:
        return True
    else:
        raise ValidationException("'%s' is not fixed" % datum)
  elif schema_type == 'enum':
    if datum in expected_schema.symbols:
        return True
    else:
        raise ValidationException("'%s'\n is not a valid enum symbol\n %s" % (pprint.pformat(datum), pprint.pformat(expected_schema.symbols)))
  elif schema_type == 'array':
      if (isinstance(datum, list) and
          False not in [validate(expected_schema.items, d) for d in datum]):
          return True
      else:
          raise ValidationException("'%s'\n is not a valid list item\n %s" % (pprint.pformat(datum), expected_schema.items))
  elif schema_type == 'map':
      if (isinstance(datum, dict) and
                 False not in [isinstance(k, basestring) for k in datum.keys()] and
                 False not in
                 [validate(expected_schema.values, v) for v in datum.values()]):
          return True
      else:
          raise ValidationException("'%s' is not a valid map value %s" % (pprint.pformat(datum), pprint.pformat(expected_schema.values)))
  elif schema_type in ['union', 'error_union']:
      if True in [validate(s, datum) for s in expected_schema.schemas]:
          return True
      else:
          raise ValidationException("'%s' is not a valid union %s" % (pprint.pformat(datum), pprint.pformat(expected_schema.schemas)))
  elif schema_type in ['record', 'error', 'request']:
      if (isinstance(datum, dict) and
                 False not in
                 [validate(f.type, datum.get(f.name)) for f in expected_schema.fields]):
          return True
      else:
          if not isinstance(datum, dict):
              raise ValidationException("'%s'\n is not a dict" % pprint.pformat(datum))
          try:
              [validate_ex(f.type, datum.get(f.name)) for f in expected_schema.fields]
          except ValidationException as v:
              raise ValidationException("%s\nValidating record %s" % (v, pprint.pformat(datum)))
  raise ValidationException("Unrecognized schema_type %s" % schema_type)

class Builder(object):
    def jseval(self, expression, context):
        if isinstance(expression, list):
            exp = "{return %s(%s);}" % (expression[0], ",".join([self.do_eval(e) for e in expression[1:]]))
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
                with open(os.path.join(basedir, ex["ref"]), "r") as f:
                    return f.read()
        else:
            return ex

    def bind_input(self, schema, datum, key):
        bindings = []

        # Handle union types
        if isinstance(schema["type"], list):
            for t in schema["type"]:
                if validate(t, datum):
                    return bind_input(t, datum)
            raise ValidationException("'%s' is not a valid union %s" % (pprint.pformat(datum), pprint.pformat(schema["type"])))

        if isinstance(schema["type"], dict):
            bindings.extend(self.bind_input(schema["type"], datum, key))

        if schema["type"] == "record":
            for f in schema["fields"]:
                bindings.extend(self.bind_input(f, datum[f["name"]], f["name"]))

        if schema["type"] == "map":
            for v in datum:
                bindings.extend(self.bind_input(schema["values"], datum[v], v))

        if schema["type"] == "array":
            for n, item in enumerate(datum):
                #print n, item, schema["items"]
                b = self.bind_input({"type": schema["items"], "binding": schema.get("binding")}, item, format(n, '06'))
                bindings.extend(b)

        if schema["type"] == "File":
            self.files.append(datum["path"])

        if "binding" in schema and isinstance(schema["binding"], dict):
            b = copy.copy(schema["binding"])

            if b.get("position"):
                b["position"] = [b["position"], key]
            else:
                b["position"] = [0, key]

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
        if self.tool.get("schemaDefs"):
            for i in self.tool["schemaDefs"]:
                avro.schema.make_avsc_object(i, self.names)

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
        builder.files = []
        builder.bindings = [{
                "position": [-1000000],
                "valueFrom": self.tool["baseCommand"]
            }]

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

        builder.bindings.extend(builder.bind_input(self.inputs_record_schema, joborder, ""))
        builder.bindings.sort(key=lambda a: a["position"])

        builder.pathmapper = PathMapper(builder.files, basedir)

        #pprint.pprint(builder.bindings)
        #pprint.pprint(builder.files)


        j = Job()
        j.joborder = joborder
        j.tool = self
        j.container = None
        j.command_line = flatten(map(builder.generate_arg, builder.bindings))
