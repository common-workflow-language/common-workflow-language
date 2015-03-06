import pprint

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
