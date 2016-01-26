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
from aslist import aslist
import jsonld_context
import schema_salad.schema

_logger = logging.getLogger("salad")

salad_files = ('metaschema.yml',
              'salad.md',
              'field_name.yml',
              'import_include.md',
              'link_res.yml',
              'ident_res.yml',
              'vocab_res.yml',
              'vocab_res.yml',
              'field_name_schema.yml',
              'field_name_src.yml',
              'field_name_proc.yml',
              'ident_res_schema.yml',
              'ident_res_src.yml',
              'ident_res_proc.yml',
              'link_res_schema.yml',
              'link_res_src.yml',
              'link_res_proc.yml',
              'vocab_res_schema.yml',
              'vocab_res_src.yml',
              'vocab_res_proc.yml')

def get_metaschema():
    loader = ref_resolver.Loader({
        "Any": "https://w3id.org/cwl/salad#Any",
        "ArraySchema": "https://w3id.org/cwl/salad#ArraySchema",
        "DocType": "https://w3id.org/cwl/salad#DocType",
        "Documentation": "https://w3id.org/cwl/salad#Documentation",
        "EnumSchema": "https://w3id.org/cwl/salad#EnumSchema",
        "JsonldPredicate": "https://w3id.org/cwl/salad#JsonldPredicate",
        "NamedType": "https://w3id.org/cwl/salad#NamedType",
        "RecordField": "https://w3id.org/cwl/salad#RecordField",
        "RecordSchema": "https://w3id.org/cwl/salad#RecordSchema",
        "SaladEnumSchema": "https://w3id.org/cwl/salad#SaladEnumSchema",
        "SaladRecordField": "https://w3id.org/cwl/salad#SaladRecordField",
        "SaladRecordSchema": "https://w3id.org/cwl/salad#SaladRecordSchema",
        "SchemaDefinedType": "https://w3id.org/cwl/salad#SchemaDefinedType",
        "SpecializeDef": "https://w3id.org/cwl/salad#SpecializeDef",
        "_container": "https://w3id.org/cwl/salad#JsonldPredicate/_container",
        "_id": {
            "@id": "https://w3id.org/cwl/salad#_id",
            "@type": "@id",
            "identity": True
        },
        "_type": "https://w3id.org/cwl/salad#JsonldPredicate/_type",
        "abstract": "https://w3id.org/cwl/salad#SaladRecordSchema/abstract",
        "array": "https://w3id.org/cwl/salad#array",
        "boolean": "http://www.w3.org/2001/XMLSchema#boolean",
        "dct": "http://purl.org/dc/terms/",
        "doc": "sld:doc",
        "docAfter": {
            "@id": "https://w3id.org/cwl/salad#docAfter",
            "@type": "@id"
        },
        "docParent": {
            "@id": "https://w3id.org/cwl/salad#docParent",
            "@type": "@id"
        },
        "docChild": {
            "@id": "https://w3id.org/cwl/salad#docChild",
            "@type": "@id"
        },
        "documentRoot": "https://w3id.org/cwl/salad#SchemaDefinedType/documentRoot",
        "documentation": "https://w3id.org/cwl/salad#documentation",
        "double": "http://www.w3.org/2001/XMLSchema#double",
        "enum": "https://w3id.org/cwl/salad#enum",
        "extends": {
            "@id": "https://w3id.org/cwl/salad#extends",
            "@type": "@id"
        },
        "fields": "sld:fields",
        "float": "http://www.w3.org/2001/XMLSchema#float",
        "identity": "https://w3id.org/cwl/salad#JsonldPredicate/identity",
        "int": "http://www.w3.org/2001/XMLSchema#int",
        "items": {
            "@id": "https://w3id.org/cwl/salad#items",
            "@type": "@vocab"
        },
        "jsonldPredicate": "sld:jsonldPredicate",
        "long": "http://www.w3.org/2001/XMLSchema#long",
        "name": "@id",
        "noLinkCheck": "https://w3id.org/cwl/salad#JsonldPredicate/noLinkCheck",
        "null": "https://w3id.org/cwl/salad#null",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "record": "https://w3id.org/cwl/salad#record",
        "sld": "https://w3id.org/cwl/salad#",
        "specialize": "https://w3id.org/cwl/salad#SaladRecordSchema/specialize",
        "specializeFrom": {
            "@id": "https://w3id.org/cwl/salad#specializeFrom",
            "@type": "@id"
        },
        "specializeTo": {
            "@id": "https://w3id.org/cwl/salad#specializeTo",
            "@type": "@id"
        },
        "string": "http://www.w3.org/2001/XMLSchema#string",
        "symbols": {
            "@id": "https://w3id.org/cwl/salad#symbols",
            "@type": "@id",
            "identity": True
        },
        "type": {
            "@id": "https://w3id.org/cwl/salad#type",
            "@type": "@vocab"
        },
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    })

    for f in salad_files:
        rs = resource_stream(__name__, 'metaschema/' + f)
        loader.cache["https://w3id.org/cwl/" + f] = rs.read()
        rs.close()

    rs = resource_stream(__name__, 'metaschema/metaschema.yml')
    loader.cache["https://w3id.org/cwl/salad"] = rs.read()
    rs.close()

    j = yaml.load(loader.cache["https://w3id.org/cwl/salad"])
    j, _ = loader.resolve_all(j, "https://w3id.org/cwl/salad#")

    #pprint.pprint(j)

    (sch_names, sch_obj) = make_avro_schema(j, loader)
    if isinstance(sch_names, Exception):
        _logger.error("Metaschema error, avro was:\n%s", json.dumps(sch_obj, indent=4))
        raise sch_names
    validate_doc(sch_names, j, loader, strict=True)
    return (sch_names, j, loader)

def load_schema(schema_ref, cache=None):
    metaschema_names, metaschema_doc, metaschema_loader = get_metaschema()
    if cache is not None:
        metaschema_loader.cache = cache
    schema_doc, schema_metadata = metaschema_loader.resolve_ref(schema_ref, "")

    validate_doc(metaschema_names, schema_doc, metaschema_loader, True)
    metactx = schema_metadata.get("@context", {})
    metactx.update(schema_metadata.get("$namespaces", {}))
    (schema_ctx, rdfs) = jsonld_context.salad_to_jsonld_context(schema_doc, metactx)

    # Create the loader that will be used to load the target document.
    document_loader = ref_resolver.Loader(schema_ctx, cache=cache)

    # Make the Avro validation that will be used to validate the target document
    (avsc_names, avsc_obj) = schema_salad.schema.make_avro_schema(schema_doc, document_loader)

    return document_loader, avsc_names, schema_metadata

def load_and_validate(document_loader, avsc_names, document, strict):
    if isinstance(document, dict):
        data, metadata = document_loader.resolve_all(document, document["id"])
    else:
        data, metadata = document_loader.resolve_ref(document)

    document_loader.validate_links(data)
    validate_doc(avsc_names, data, document_loader, strict)
    return data, metadata

def validate_doc(schema_names, validate_doc, loader, strict):
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

    anyerrors = []
    for pos, item in enumerate(validate_doc):
        errors = []
        success = False
        for r in schema_names.names.values():
            if r.get_prop("documentRoot"):
                try:
                    validate.validate_ex(r, item, loader.identifiers, strict, foreign_properties=loader.foreign_properties)
                    success = True
                    break
                except validate.ValidationException as e:
                    errors.append("Could not validate as `%s` because\n%s" % (r.get_prop("name"), validate.indent(str(e), nolead=False)))
        if not success:
            objerr = "Validation error at position %i" % pos
            for ident in loader.identifiers:
                if ident in item:
                    objerr = "Validation error in object %s" % (item[ident])
                    break
            anyerrors.append("%s\n%s" % (objerr, validate.indent("\n".join(errors))))
    if anyerrors:
        raise validate.ValidationException("\n".join(anyerrors))


def replace_type(items, spec, loader, found):
    """ Go through and replace types in the 'spec' mapping"""

    items = copy.deepcopy(items)
    if isinstance(items, dict):
        # recursively check these fields for types to replace
        if "type" in items and items["type"] in ("record", "enum"):
            if items.get("name"):
                if items["name"] in found:
                    return items["name"]
                else:
                    found.add(items["name"])

        for n in ("type", "items", "fields"):
            if n in items:
                items[n] = replace_type(items[n], spec, loader, found)
                if isinstance(items[n], list):
                    items[n] = flatten(items[n])

        return items
    elif isinstance(items, list):
        # recursively transform list
        return [replace_type(i, spec, loader, found) for i in items]
    elif isinstance(items, basestring):
        # found a string which is a symbol corresponding to a type.
        replace_with = None
        if items in loader.vocab:
            # If it's a vocabulary term, first expand it to its fully qualified URI
            items = loader.vocab[items]

        if items in spec:
            # Look up in specialization map
            replace_with = spec[items]

        if replace_with:
            return replace_type(replace_with, spec, loader, found)
    return items

def avro_name(url):
    doc_url, frg = urlparse.urldefrag(url)
    if frg:
        if '/' in frg:
            return frg[frg.rindex('/')+1:]
        else:
            return frg
    return url

def make_valid_avro(items, alltypes, found, union=False):
    items = copy.deepcopy(items)
    if isinstance(items, dict):
        if items.get("name"):
            items["name"] = avro_name(items["name"])

        if "type" in items and items["type"] in ("https://w3id.org/cwl/salad#record", "https://w3id.org/cwl/salad#enum", "record", "enum"):
            if items.get("abstract"):
                return items
            if not items.get("name"):
                raise Exception("Named schemas must have a non-empty name: %s" % items)

            if items["name"] in found:
                return items["name"]
            else:
                found.add(items["name"])
        for n in ("type", "items", "values", "fields"):
            if n in items:
                items[n] = make_valid_avro(items[n], alltypes, found, union=True)
        if "symbols" in items:
            items["symbols"] = [avro_name(sym) for sym in items["symbols"]]
        return items
    if isinstance(items, list):
        n = []
        for i in items:
            n.append(make_valid_avro(i, alltypes, found, union=union))
        return n
    if union and isinstance(items, basestring):
        if items in alltypes and avro_name(items) not in found:
            return make_valid_avro(alltypes[items], alltypes, found, union=union)
        items = avro_name(items)
    return items


def extend_and_specialize(items, loader):
    """Apply 'extend' and 'specialize' to fully materialize derived record
    types."""

    types = {t["name"]: t for t in items}
    n = []

    for t in items:
        t = copy.deepcopy(t)
        if "extends" in t:
            if "specialize" in t:
                spec = {sp["specializeFrom"]: sp["specializeTo"] for sp in aslist(t["specialize"])}
            else:
                spec = {}

            exfields = []
            exsym = []
            for ex in aslist(t["extends"]):
                if ex not in types:
                    raise Exception("Extends %s in %s refers to invalid base type" % (t["extends"], t["name"]))

                basetype = copy.deepcopy(types[ex])

                if t["type"] == "record":
                    if spec:
                        basetype["fields"] = replace_type(basetype.get("fields", []), spec, loader, set())

                    for f in basetype.get("fields", []):
                        if "inherited_from" not in f:
                            f["inherited_from"] = ex

                    exfields.extend(basetype.get("fields", []))
                elif t["type"] == "enum":
                    exsym.extend(basetype.get("symbols", []))

            if t["type"] == "record":
                exfields.extend(t.get("fields", []))
                t["fields"] = exfields

                fieldnames = set()
                for field in t["fields"]:
                    if field["name"] in fieldnames:
                        raise validate.ValidationException("Field name %s appears twice in %s" % (field["name"], t["name"]))
                    else:
                        fieldnames.add(field["name"])

                for y in [x for x in t["fields"] if x["name"] == "class"]:
                    y["type"] = {"type": "enum",
                                 "symbols": [r["name"]],
                                 "name": r["name"]+"_class",
                    }
                    y["doc"] = "Must be `%s` to indicate this is a %s object." % (r["name"], r["name"])
            elif t["type"] == "enum":
                exsym.extend(t.get("symbols", []))
                t["symbol"] = exsym

            types[t["name"]] = t

        n.append(t)

    ex_types = {t["name"]: t for t in n}

    extended_by = {}
    for t in n:
        if "extends" in t:
            for ex in aslist(t["extends"]):
                if ex_types[ex].get("abstract"):
                    add_dictlist(extended_by, ex, ex_types[t["name"]])
                    add_dictlist(extended_by, avro_name(ex), ex_types[ex])

    for t in n:
        if "fields" in t:
            t["fields"] = replace_type(t["fields"], extended_by, loader, set())

    return n

def make_avro_schema(j, loader):
    names = avro.schema.Names()

    #pprint.pprint(j)

    j = extend_and_specialize(j, loader)

    j2 = make_valid_avro(j, {t["name"]: t for t in j}, set())

    j3 = [t for t in j2 if isinstance(t, dict) and not t.get("abstract") and t.get("type") != "documentation"]

    try:
        avro.schema.make_avsc_object(j3, names)
    except avro.schema.SchemaParseException as e:
        names = e

    return (names, j3)
