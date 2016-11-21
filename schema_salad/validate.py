import pprint
import avro.schema
from avro.schema import Schema
import sys
import urlparse
import re
from typing import Any, Union
from .sourceline import SourceLine, lineno_re, bullets, indent


class ValidationException(Exception):
    pass


class ClassValidationException(ValidationException):
    pass


def validate(expected_schema,           # type: Schema
             datum,                     # type: Any
             identifiers=set(),         # type: Set[unicode]
             strict=False,              # type: bool
             foreign_properties=set()   # type: Set[unicode]
             ):
    # type: (...) -> bool
    return validate_ex(
        expected_schema, datum, identifiers, strict=strict,
        foreign_properties=foreign_properties, raise_ex=False)


INT_MIN_VALUE = -(1 << 31)
INT_MAX_VALUE = (1 << 31) - 1
LONG_MIN_VALUE = -(1 << 63)
LONG_MAX_VALUE = (1 << 63) - 1


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


def vpformat(datum):  # type: (Any) -> str
    a = pprint.pformat(datum)
    if len(a) > 160:
        a = a[0:160] + "[...]"
    return a


def validate_ex(expected_schema,            # type: Schema
                datum,                      # type: Any
                identifiers=None,           # type: Set[unicode]
                strict=False,               # type: bool
                foreign_properties=None,    # type: Set[unicode]
                raise_ex=True               # type: bool
                ):
    # type: (...) -> bool
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
                raise ValidationException(u"the value is not null")
            else:
                return False
    elif schema_type == 'boolean':
        if isinstance(datum, bool):
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value is not boolean")
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
                raise ValidationException(u"the value is not string")
            else:
                return False
    elif schema_type == 'bytes':
        if isinstance(datum, str):
            return True
        else:
            if raise_ex:
                raise ValidationException(
                    u"the value `%s` is not bytes" % vpformat(datum))
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
                raise ValidationException(
                    u"the value `%s` is not long" % vpformat(datum))
            else:
                return False
    elif schema_type in ['float', 'double']:
        if (isinstance(datum, int) or isinstance(datum, long)
                or isinstance(datum, float)):
            return True
        else:
            if raise_ex:
                raise ValidationException(
                    u"the value `%s` is not float or double" % vpformat(datum))
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
        if not isinstance(datum, basestring):
            if raise_ex:
                raise ValidationException(
                    u"value is a %s but expected a string" % (type(datum).__name__))
            else:
                return False
        if datum in expected_schema.symbols:
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value %s is not a valid %s, expected %s%s" % (vpformat(datum), expected_schema.name,
                                                                                              "one of " if len(
                                                                                                  expected_schema.symbols) > 1 else "",
                                                                                              "'" + "', '".join(expected_schema.symbols) + "'"))
            else:
                return False
    elif isinstance(expected_schema, avro.schema.ArraySchema):
        if isinstance(datum, list):
            for i, d in enumerate(datum):
                try:
                    sl = SourceLine(datum, i, ValidationException)
                    if not validate_ex(expected_schema.items, d, identifiers, strict=strict,
                                       foreign_properties=foreign_properties,
                                       raise_ex=raise_ex):
                        return False
                except ValidationException as v:
                    if raise_ex:
                        raise sl.makeError(
                            unicode("item is invalid because\n%s" % (indent(str(v)))))
                    else:
                        return False
            return True
        else:
            if raise_ex:
                raise ValidationException(u"the value is not a list, expected list of %s" % (
                    friendly(expected_schema.items)))
            else:
                return False
    elif isinstance(expected_schema, avro.schema.UnionSchema):
        for s in expected_schema.schemas:
            if validate_ex(s, datum, identifiers, strict=strict, raise_ex=False):
                return True

        if not raise_ex:
            return False

        errors = []  # type: List[unicode]
        checked = []
        for s in expected_schema.schemas:
            if isinstance(datum, list) and not isinstance(s, avro.schema.ArraySchema):
                continue
            elif isinstance(datum, dict) and not isinstance(s, avro.schema.RecordSchema):
                continue
            elif isinstance(datum, (bool, int, long, float, basestring)) and isinstance(s, (avro.schema.ArraySchema, avro.schema.RecordSchema)):
                continue
            elif datum is not None and s.type == "null":
                continue

            checked.append(s)
            try:
                validate_ex(s, datum, identifiers, strict=strict,
                            foreign_properties=foreign_properties, raise_ex=True)
            except ClassValidationException as e:
                raise
            except ValidationException as e:
                errors.append(unicode(e))
        if errors:
            raise ValidationException(bullets(["tried %s but\n%s" % (friendly(
                checked[i]), indent(errors[i])) for i in range(0, len(errors))], "- "))
        else:
            raise ValidationException("value is a %s, expected %s" % (
                type(datum).__name__, friendly(expected_schema)))

    elif isinstance(expected_schema, avro.schema.RecordSchema):
        if not isinstance(datum, dict):
            if raise_ex:
                raise ValidationException(u"is not a dict")
            else:
                return False

        classmatch = None
        for f in expected_schema.fields:
            if f.name in ("class",):
                d = datum.get(f.name)
                if not d:
                    if raise_ex:
                        raise ValidationException(
                            u"Missing '%s' field" % (f.name))
                    else:
                        return False
                if expected_schema.name != d:
                    return False
                classmatch = d
                break

        errors = []
        for f in expected_schema.fields:
            if f.name in ("class",):
                continue

            if f.name in datum:
                fieldval = datum[f.name]
            else:
                try:
                    fieldval = f.default
                except KeyError:
                    fieldval = None

            try:
                sl = SourceLine(datum, f.name, unicode)
                if not validate_ex(f.type, fieldval, identifiers, strict=strict, foreign_properties=foreign_properties,
                                   raise_ex=raise_ex):
                    return False
            except ValidationException as v:
                if f.name not in datum:
                    errors.append(u"missing required field `%s`" % f.name)
                else:
                    errors.append(sl.makeError(u"the `%s` field is not valid because\n%s" % (
                        f.name, indent(str(v)))))

        if strict:
            for d in datum:
                found = False
                for f in expected_schema.fields:
                    if d == f.name:
                        found = True
                if not found:
                    sl = SourceLine(datum, d, unicode)
                    if d not in identifiers and d not in foreign_properties and d[0] not in ("@", "$"):
                        if not raise_ex:
                            return False
                        split = urlparse.urlsplit(d)
                        if split.scheme:
                            errors.append(sl.makeError(
                                u"unrecognized extension field `%s` and strict is True.  Did you include a $schemas section?" % (d)))
                        else:
                            errors.append(sl.makeError(u"invalid field `%s`, expected one of: %s" % (
                                d, ", ".join("'%s'" % fn.name for fn in expected_schema.fields))))

        if errors:
            if raise_ex:
                if classmatch:
                    raise ClassValidationException(bullets(errors, "* "))
                else:
                    raise ValidationException(bullets(errors, "* "))
            else:
                return False
        else:
            return True
    if raise_ex:
        raise ValidationException(u"Unrecognized schema_type %s" % schema_type)
    else:
        return False
