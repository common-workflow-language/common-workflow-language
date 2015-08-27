import avro
import copy
from  makedoc import add_dictlist
import sys
import pprint
from pkg_resources import resource_stream
import yaml
import avro.schema
import validate
import json
import urlparse
import ref_resolver
from flatten import flatten
import logging

_logger = logging.getLogger("salad")

def get_metaschema():
    f = resource_stream(__name__, 'metaschema.yml')

    loader = ref_resolver.Loader({
        "Any": "https://w3id.org/cwl/salad#Any",
        "ArraySchema": "https://w3id.org/cwl/salad#ArraySchema",
        "ComplexType": "https://w3id.org/cwl/salad#ComplexType",
        "Documentation": "https://w3id.org/cwl/salad#Documentation",
        "EnumSchema": "https://w3id.org/cwl/salad#EnumSchema",
        "JsonldPredicate": "https://w3id.org/cwl/salad#JsonldPredicate",
        "RecordField": "https://w3id.org/cwl/salad#RecordField",
        "RecordSchema": "https://w3id.org/cwl/salad#RecordSchema",
        "SpecializeDef": "https://w3id.org/cwl/salad#SpecializeDef",
        "_container": "https://w3id.org/cwl/salad#_container",
        "_id": {
            "@id": "https://w3id.org/cwl/salad#_id",
            "@type": "@id",
            "identity": True
        },
        "_type": "https://w3id.org/cwl/salad#_type",
        "abstract": "https://w3id.org/cwl/salad#abstract",
        "array": "https://w3id.org/cwl/avro#array",
        "avro": "https://w3id.org/cwl/avro#",
        "boolean": "https://w3id.org/cwl/avro#boolean",
        "bytes": "https://w3id.org/cwl/avro#bytes",
        "dct": "http://purl.org/dc/terms/",
        "doc": "https://w3id.org/cwl/salad#doc",
        "docAfter": {
            "@id": "https://w3id.org/cwl/salad#docAfter",
            "@type": "@id"
        },
        "docParent": {
            "@id": "https://w3id.org/cwl/salad#docParent",
            "@type": "@id"
        },
        "documentRoot": "https://w3id.org/cwl/salad#documentRoot",
        "documentation": "https://w3id.org/cwl/salad#documentation",
        "double": "https://w3id.org/cwl/avro#double",
        "enum": "https://w3id.org/cwl/avro#enum",
        "extends": {
            "@id": "https://w3id.org/cwl/salad#extends",
            "@type": "@id"
        },
        "fields": "avro:fields",
        "float": "https://w3id.org/cwl/avro#float",
        "identity": "https://w3id.org/cwl/salad#identity",
        "int": "https://w3id.org/cwl/avro#int",
        "items": {
            "@id": "https://w3id.org/cwl/avro#items",
            "@type": "@vocab"
        },
        "jsonldPredicate": "https://w3id.org/cwl/salad#jsonldPredicate",
        "jsonldPrefix": "https://w3id.org/cwl/salad#jsonldPrefix",
        "long": "https://w3id.org/cwl/avro#long",
        "name": "@id",
        "null": "https://w3id.org/cwl/avro#null",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "record": "https://w3id.org/cwl/avro#record",
        "sld": "https://w3id.org/cwl/salad#",
        "specialize": "https://w3id.org/cwl/salad#specialize",
        "specializeFrom": {
            "@id": "https://w3id.org/cwl/salad#specializeFrom",
            "@type": "@id"
        },
        "specializeTo": {
            "@id": "https://w3id.org/cwl/salad#specializeTo",
            "@type": "@id"
        },
        "string": "https://w3id.org/cwl/avro#string",
        "symbols": {
            "@id": "https://w3id.org/cwl/avro#symbols",
            "@type": "@id",
            "identity": True
        },
        "type": {
            "@id": "https://w3id.org/cwl/avro#type",
            "@type": "@vocab"
        }
    })
    j = yaml.load(f)
    j = loader.resolve_all(j, "https://w3id.org/cwl/salad#")

    #pprint.pprint(j)

    (sch_names, sch_obj) = make_avro_schema(j)
    validate_doc(sch_names, j, strict=True)
    return (sch_names, j, loader)


def validate_doc(schema_names, validate_doc, strict):
    has_root = False
    for r in schema_names.names.values():
        if r.get_prop("documentRoot"):
            has_root = True
            break

    if not has_root:
        raise validate.ValidationException("No document roots defined in the schema")

    if isinstance(validate_doc, list):
        pass
    elif isinstance(validate_doc, dict):
        validate_doc = [validate_doc]
    else:
        raise validate.ValidationException("Document must be dict or list")

    for item in validate_doc:
        errors = []
        success = False
        for r in schema_names.names.values():
            if r.get_prop("documentRoot"):
                try:
                    validate.validate_ex(r, item, strict)
                    success = True
                    break
                except validate.ValidationException as e:
                    errors.append("Could not validate as %s because %s" % (r.get_prop("name"), str(e)))
        if not success:
            raise validate.ValidationException("- %s" % ("\n\n- ".join(errors)))


def replace_type(items, spec):
    if isinstance(items, dict):
        for n in ("type", "items"):
            if n in items:
                items[n] = replace_type(items[n], spec)
                if isinstance(items[n], list):
                    items[n] = flatten(items[n])
        return items
    if isinstance(items, list):
        n = []
        for i in items:
            n.append(replace_type(i, spec))
        return n
    if isinstance(items, basestring):
        if items in spec:
            return spec[items]
    return items

def avro_name(url):
    doc_url, frg = urlparse.urldefrag(url)
    if frg:
        if '/' in frg:
            return frg[frg.rindex('/')+1:]
        else:
            return frg
    return url

def make_valid_avro(items, found, union=False):
    items = copy.deepcopy(items)
    if isinstance(items, dict):
        if "name" in items:
            items["name"] = avro_name(items["name"])

        if "type" in items and items["type"] in ("record", "enum"):
            if items.get("abstract"):
                return items
            if "name" not in items:
                raise Exception("Named schemas must have a non-empty name: %s" % items)
            if items["name"] in found:
                return items["name"]
            else:
                found.add(items["name"])
        for n in ("type", "items", "values", "fields", "symbols"):
            if n in items:
                items[n] = make_valid_avro(items[n], found, union=True)
        return items
    if isinstance(items, list):
        n = []
        for i in items:
            n.append(make_valid_avro(i, found, union=union))
        return n
    if union and isinstance(items, basestring):
        doc_url, frg = urlparse.urldefrag(items)
        if frg:
            items = frg
    return items

def aslist(l):
    if isinstance(l, list):
        return l
    else:
        return [l]

def extend_and_specialize(items):
    types = {t["name"]: t for t in items}
    n = []

    for t in items:
        if "extends" in t:
            if t["extends"] not in types:
                raise Exception("Extends %s in %s refers to invalid base type" % (t["extends"], t["name"]))

            r = copy.deepcopy(types[t["extends"]])

            r["name"] = t["name"]
            if "specialize" in t:
                spec = {sp["specializeFrom"]: sp["specializeTo"] for sp in aslist(t["specialize"])}
                r["fields"] = replace_type(r["fields"], spec)

            for f in r["fields"]:
                if "inherited_from" not in f:
                    f["inherited_from"] = t["extends"]

            r["fields"].extend(t.get("fields", []))

            for y in [x for x in r["fields"] if x["name"] == "class"]:
                y["type"] = {"type": "enum",
                             "symbols": [r["name"]],
                             "name": r["name"]+"_class",
                }
                y["doc"] = "Must be `%s` to indicate this is a %s object." % (r["name"], r["name"])

            r["extends"] = t["extends"]
            r["documentRoot"] = t.get("documentRoot", r.get("documentRoot"))
            r["abstract"] = t.get("abstract", False)
            r["doc"] = t.get("doc", "")
            types[t["name"]] = r
            t = r

        n.append(t)

    ex_types = {t["name"]: t for t in n}

    extended_by = {}
    for t in n:
        if "extends" in t and ex_types[t["extends"]].get("abstract"):
            add_dictlist(extended_by, t["extends"], ex_types[t["name"]])
            add_dictlist(extended_by, avro_name(t["extends"]), ex_types[t["name"]])

    for t in n:
        if "fields" in t:
            t["fields"] = replace_type(t["fields"], extended_by)

    n = replace_type(n, ex_types)

    return n

def make_avro_schema(j):
    names = avro.schema.Names()

    #pprint.pprint(j)

    j = extend_and_specialize(j)

    #pprint.pprint(j)

    j2 = make_valid_avro(j, set())

    j3 = [t for t in j2 if isinstance(t, dict) and not t.get("abstract") and t.get("type") != "documentation"]

    avro.schema.make_avsc_object(j3, names)

    return (names, j3)
