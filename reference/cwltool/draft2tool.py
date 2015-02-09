import avro.schema
import json
import pprint

module_dir = os.path.dirname(os.path.abspath(__file__))
names = avro.schema.Names()
cwl_avsc = os.path.join(module_dir, 'schemas/draft-2/cwl.avsc')
with open(cwl_avsc) as f:
    j = json.load(f)
    for t in j:
        avro.schema.make_avsc_object(t, names)

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
          [validate_ex(f.type, datum.get(f.name)) for f in expected_schema.fields]
  raise ValidationException("Unrecognized schema_type %s" % schema_type)

def validate_tool(j):
    validate_ex(names.get_name("CommandLineTool", ""), j)
