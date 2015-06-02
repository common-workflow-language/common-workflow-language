import pprint
import avro.schema

class ValidationException(Exception):
    pass

def validate(expected_schema, datum, strict=False):
    try:
        return validate_ex(expected_schema, datum, strict=strict)
    except ValidationException:
        return False

INT_MIN_VALUE = -(1 << 31)
INT_MAX_VALUE = (1 << 31) - 1
LONG_MIN_VALUE = -(1 << 63)
LONG_MAX_VALUE = (1 << 63) - 1

def indent(v, nolead=False):
    if nolead:
        return v.splitlines()[0] + "\n".join(["  " + l for l in v.splitlines()[1:]])
    else:
        return "\n".join(["  " + l for l in v.splitlines()])

def friendly(v):
    if isinstance(v, avro.schema.NamedSchema):
        return v.name
    if isinstance(v, avro.schema.ArraySchema):
        return "array of <%s>" % friendly(v.items)
    elif isinstance(v, avro.schema.PrimitiveSchema):
        return v.type
    elif isinstance(v, avro.schema.UnionSchema):
        return " or ".join([friendly(s) for s in v.schemas])
    else:
        return v

def multi(v, q=""):
    if '\n' in v:
        return "%s%s%s\n" % (q, v, q)
    else:
        return "%s%s%s" % (q, v, q)

def validate_ex(expected_schema, datum, strict=False):
    """Determine if a python datum is an instance of a schema."""

    schema_type = expected_schema.type

    if schema_type == 'null':
        if datum is None:
            return True
        else:
            raise ValidationException("the value `%s` is not null" % pprint.pformat(datum))
    elif schema_type == 'boolean':
        if isinstance(datum, bool):
            return True
        else:
            raise ValidationException("the value `%s` is not boolean" % pprint.pformat(datum))
    elif schema_type == 'string':
        if isinstance(datum, basestring):
            return True
        else:
            raise ValidationException("the value `%s` is not string" % pprint.pformat(datum))
    elif schema_type == 'bytes':
        if isinstance(datum, str):
            return True
        else:
            raise ValidationException("the value `%s` is not bytes" % pprint.pformat(datum))
    elif schema_type == 'int':
        if ((isinstance(datum, int) or isinstance(datum, long))
            and INT_MIN_VALUE <= datum <= INT_MAX_VALUE):
            return True
        else:
            raise ValidationException("`%s` is not int" % pprint.pformat(datum))
    elif schema_type == 'long':
        if ((isinstance(datum, int) or isinstance(datum, long))
            and LONG_MIN_VALUE <= datum <= LONG_MAX_VALUE):
            return True
        else:
            raise ValidationException("the value `%s` is not long" % pprint.pformat(datum))
    elif schema_type in ['float', 'double']:
        if (isinstance(datum, int) or isinstance(datum, long)
            or isinstance(datum, float)):
            return True
        else:
            raise ValidationException("the value `%s` is not float or double" % pprint.pformat(datum))
    elif schema_type == 'fixed':
        if isinstance(datum, str) and len(datum) == expected_schema.size:
            return True
        else:
            raise ValidationException("the value `%s` is not fixed" % pprint.pformat(datum))
    elif schema_type == 'enum':
        if expected_schema.name == "Any":
            if datum is not None:
                return True
            else:
                raise ValidationException("Any type must be non-null")
        if datum in expected_schema.symbols:
            return True
        else:
            raise ValidationException("the value `%s`\n is not a valid enum symbol, expected\n %s" % (pprint.pformat(datum), pprint.pformat(expected_schema.symbols)))
    elif schema_type == 'array':
        if isinstance(datum, list):
            for i, d in enumerate(datum):
                try:
                    validate_ex(expected_schema.items, d, strict=strict)
                except ValidationException as v:
                    raise ValidationException("At position %i\n%s" % (i, indent(str(v))))
            return True
        else:
            raise ValidationException("the value `%s` is not a list, expected list of %s" % (pprint.pformat(datum), friendly(expected_schema.items)))
    elif schema_type == 'map':
        if (isinstance(datum, dict) and
            False not in [isinstance(k, basestring) for k in datum.keys()] and
            False not in [validate(expected_schema.values, v, strict=strict) for v in datum.values()]):
            return True
        else:
            raise ValidationException("`%s` is not a valid map value, expected\n %s" % (pprint.pformat(datum), pprint.pformat(expected_schema.values)))
    elif schema_type in ['union', 'error_union']:
        if True in [validate(s, datum, strict=strict) for s in expected_schema.schemas]:
            return True
        else:
            errors = []
            for s in expected_schema.schemas:
                try:
                    validate_ex(s, datum, strict=strict)
                except ValidationException as e:
                    errors.append(str(e))
            raise ValidationException("the value %s is not a valid type in the union, expected one of:\n%s" % (multi(pprint.pformat(datum), '`'),
                                                                                     "\n".join(["- %s, but\n %s" % (friendly(expected_schema.schemas[i]), indent(multi(errors[i]))) for i in range(0, len(expected_schema.schemas))])))

    elif schema_type in ['record', 'error', 'request']:
        if not isinstance(datum, dict):
            raise ValidationException("`%s`\n is not a dict" % pprint.pformat(datum))

        errors = []
        for f in expected_schema.fields:
            try:
                validate_ex(f.type, datum.get(f.name), strict=strict)
            except ValidationException as v:
                if f.name not in datum:
                    errors.append("missing required field `%s`" % f.name)
                else:
                    errors.append("could not validate field `%s` because\n%s" % (f.name, multi(indent(str(v)))))
        if strict:
            for d in datum:
                found = False
                for f in expected_schema.fields:
                    if d == f.name:
                        found = True
                if not found:
                    errors.append("could not validate field `%s` because it is not recognized and strict is True" % d)
        if errors:
            raise ValidationException("\n".join(errors))
        else:
            return True
    raise ValidationException("Unrecognized schema_type %s" % schema_type)
