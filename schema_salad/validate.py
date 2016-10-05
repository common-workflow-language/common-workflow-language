import pprint
import avro.schema
import sys
import urlparse
from typing import Any, Union

class ValidationException(Exception):
    pass

class ClassValidationException(ValidationException):
    pass

def validate(expected_schema, datum, identifiers=set(), strict=False, foreign_properties=set()):
    # type: (avro.schema.Schema, Any, Set[unicode], bool, Set[unicode]) -> bool
    return validate_ex(expected_schema, datum, identifiers, strict=strict, foreign_properties=foreign_properties, raise_ex=False)

INT_MIN_VALUE = -(1 << 31)
INT_MAX_VALUE = (1 << 31) - 1
LONG_MIN_VALUE = -(1 << 63)
LONG_MAX_VALUE = (1 << 63) - 1

def indent(v, nolead=False):  # type: (Union[str, unicode], bool) -> unicode
    if nolead:
        return v.splitlines()[0] + u"\n".join([u"  " + l for l in v.splitlines()[1:]])
    else:
        return u"\n".join(["  " + l for l in v.splitlines()])

def friendly(v):  # type: (Any) -> Any
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

def multi(v, q=""):  # type: (Union[str, unicode], Union[str, unicode]) -> unicode
    if '\n' in v:
        return u"%s%s%s\n" % (q, v, q)
    else:
        return u"%s%s%s" % (q, v, q)

def vpformat(datum):  # type: (Any) -> str
    a = pprint.pformat(datum)
    if len(a) > 160:
        a = a[0:160] + "[...]"
    return a

def validate_ex(expected_schema, datum, identifiers=None, strict=False,
                foreign_properties=None, raise_ex=True):
    # type: (avro.schema.Schema, Any, Set[unicode], bool, Set[unicode], bool) -> bool
    """Determine if a python datum is an instance of a schema."""

    if not identifiers:
        identifiers = set()

    if not foreign_properties:
        foreign_properties = set()

    schema_type = expected_schema.type

    if schema_type == 'null':
        if datum is None:
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s` is not null" % vpformat(datum))
            else:
                return False
    elif schema_type == 'boolean':
        if isinstance(datum, bool):
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s` is not boolean" % vpformat(datum))
            else:
                return False
    elif schema_type == 'string':
        if isinstance(datum, basestring):
            return True
        elif isinstance(datum, bytes):
            datum = datum.decode(u"utf-8")
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s` is not string" % vpformat(datum))
            else:
                return False
    elif schema_type == 'bytes':
        if isinstance(datum, str):
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s` is not bytes" % vpformat(datum))
            else:
                return False
    elif schema_type == 'int':
        if ((isinstance(datum, int) or isinstance(datum, long))
            and INT_MIN_VALUE <= datum <= INT_MAX_VALUE):
            return True
        else:
            if raise_ex:
                raise ValidationException(u"`%s` is not int" % vpformat(datum))
            else:
                return False
    elif schema_type == 'long':
        if ((isinstance(datum, int) or isinstance(datum, long))
            and LONG_MIN_VALUE <= datum <= LONG_MAX_VALUE):
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s` is not long" % vpformat(datum))
            else:
                return False
    elif schema_type in ['float', 'double']:
        if (isinstance(datum, int) or isinstance(datum, long)
            or isinstance(datum, float)):
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s` is not float or double" % vpformat(datum))
            else:
                return False
    elif isinstance(expected_schema, avro.schema.FixedSchema):
        if isinstance(datum, str) and len(datum) == expected_schema.size:
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s` is not fixed" % vpformat(datum))
            else:
                return False
    elif isinstance(expected_schema, avro.schema.EnumSchema):
        if expected_schema.name == "Any":
            if datum is not None:
                return True
            else:
                if raise_ex:
                    raise ValidationException(u"'Any' type must be non-null")
                else:
                    return False
        if datum in expected_schema.symbols:
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s`\n is not a valid symbol in enum %s, expected one of %s" % (vpformat(datum), expected_schema.name, "'" + "', '".join(expected_schema.symbols) + "'"))
            else:
                return False
    elif isinstance(expected_schema, avro.schema.ArraySchema):
        if isinstance(datum, list):
            for i, d in enumerate(datum):
                try:
                    if not validate_ex(expected_schema.items, d, identifiers, strict=strict, foreign_properties=foreign_properties, raise_ex=raise_ex):
                        return False
                except ValidationException as v:
                    if raise_ex:
                        raise ValidationException(u"At position %i\n%s" % (i, indent(str(v))))
                    else:
                        return False
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value `%s` is not a list, expected list of %s" % (vpformat(datum), friendly(expected_schema.items)))
            else:
                return False
    elif isinstance(expected_schema, avro.schema.UnionSchema):
        for s in expected_schema.schemas:
            if validate_ex(s, datum, identifiers, strict=strict, raise_ex=False):
                return True

        if not raise_ex:
            return False

        errors = []  # type: List[unicode]
        for s in expected_schema.schemas:
            try:
                validate_ex(s, datum, identifiers, strict=strict, foreign_properties=foreign_properties, raise_ex=True)
            except ClassValidationException as e:
                raise
            except ValidationException as e:
                errors.append(unicode(e))

        raise ValidationException(u"the value %s is not a valid type in the union, expected one of:\n%s" % (
            multi(vpformat(datum), '`'), u"\n".join([
                u"- %s, but\n %s" % (
                    friendly(expected_schema.schemas[i]), indent(multi(errors[i])))
                for i in range(0, len(expected_schema.schemas))])))

    elif isinstance(expected_schema, avro.schema.RecordSchema):
        if not isinstance(datum, dict):
            if raise_ex:
                raise ValidationException(u"`%s`\n is not a dict" % vpformat(datum))
            else:
                return False

        classmatch = None
        for f in expected_schema.fields:
            if f.name == "class":
                d = datum.get("class")
                if not d:
                    if raise_ex:
                        raise ValidationException(u"Missing 'class' field")
                    else:
                        return False
                if expected_schema.name != d:
                    return False
                classmatch = d
                break

        errors = []
        for f in expected_schema.fields:
            if f.name == "class":
                continue

            if f.name in datum:
                fieldval = datum[f.name]
            else:
                try:
                    fieldval = f.default
                except KeyError:
                    fieldval = None

            try:
                if not validate_ex(f.type, fieldval, identifiers, strict=strict, foreign_properties=foreign_properties, raise_ex=raise_ex):
                    return False
            except ValidationException as v:
                if f.name not in datum:
                    errors.append(u"missing required field `%s`" % f.name)
                else:
                    errors.append(u"could not validate field `%s` because\n%s" % (f.name, multi(indent(str(v)))))

        if strict:
            for d in datum:
                found = False
                for f in expected_schema.fields:
                    if d == f.name:
                        found = True
                if not found:
                    if d not in identifiers and d not in foreign_properties and d[0] not in ("@", "$"):
                        if not raise_ex:
                            return False
                        split = urlparse.urlsplit(d)
                        if split.scheme:
                            errors.append(u"could not validate extension field `%s` because it is not recognized and strict is True.  Did you include a $schemas section?" % (d))
                        else:
                            errors.append(u"could not validate field `%s` because it is not recognized and strict is True, valid fields are: %s" % (d, ", ".join(fn.name for fn in expected_schema.fields)))

        if errors:
            if raise_ex:
                if classmatch:
                    raise ClassValidationException(u"%s record %s" % (classmatch, "\n".join(errors)))
                else:
                    raise ValidationException(u"\n".join(errors))
            else:
                return False
        else:
            return True
    if raise_ex:
        raise ValidationException(u"Unrecognized schema_type %s" % schema_type)
    else:
        return False
