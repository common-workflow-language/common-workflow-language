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

def get_metaschema():
    f = resource_stream(__name__, 'metaschema.yml')

    loader = ref_resolver.Loader()
    loader.url_fields = ["type", "items", "symbols"]
    loader.vocab_fields = ["type", "items"]
    loader.checked_urls = ["type", "items"]
    loader.vocab = {
        "null": "https://w3id.org/cwl/salad#null",
        "boolean": "https://w3id.org/cwl/salad#boolean",
        "int": "https://w3id.org/cwl/salad#int",
        "long": "https://w3id.org/cwl/salad#long",
        "float": "https://w3id.org/cwl/salad#float",
        "double": "https://w3id.org/cwl/salad#double",
        "bytes": "https://w3id.org/cwl/salad#bytes",
        "string": "https://w3id.org/cwl/salad#string",
        "record": "https://w3id.org/cwl/salad#record",
        "enum": "https://w3id.org/cwl/salad#enum",
        "array": "https://w3id.org/cwl/salad#array",
        "doc": "https://w3id.org/cwl/salad#doc",
        "Any": "https://w3id.org/cwl/salad#Any"
    }
    loader.identifiers = ["name"]
    j = yaml.load(f)
    j = loader.resolve_all(j, "https://w3id.org/cwl/salad#")

    (sch_names, sch_obj) = make_avro_schema(j)

    for item in j:
        validate.validate_ex(sch_names.get_name("Schema", ""), item, strict=True)

    return (sch_names, j, loader)


def create_loader(ctx):
    loader = Loader()
    loader.url_fields = []
    loader.identifiers = []
    for c in ctx:
        if ctx[c] == "@id":
            loader.identifiers.append(c)
        elif isinstance(ctx[c], dict) and ctx[c].get("@type") == "@id":
            loader.url_fields.append(c)
    loader.checked_urls = loader.url_fields
    loader.checked_urls.remove("symbols")
    _logger.debug("url_fields is %s", loader.url_fields)
    return loader


def load_schema(f):
    _, metaschema = schema.get_metaschema()
    with open(args.schema) as f:
        j = yaml.load(f)

    (ctx, g) = jsonld_context.salad_to_jsonld_context(j)
    loader = create_loader(ctx)


def replace_type(items, spec):
    if isinstance(items, dict):
        for n in ("type", "items", "values"):
            if n in items:
                items[n] = replace_type(items[n], spec)
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

def make_valid_avro(items, found, union=False):
    items = copy.deepcopy(items)
    if isinstance(items, dict):
        if "name" in items:
            doc_url, frg = urlparse.urldefrag(items["name"])
            if frg:
                if '/' in frg:
                    items["name"] = frg[frg.rindex('/')+1:]
                else:
                    items["name"] = frg

        if "type" in items and items["type"] in ("record", "enum"):
            if items.get("abstract"):
                return items
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

def extend_and_specialize(items):
    types = {t["name"]: t for t in items}
    n = []

    for t in items:
        if "extends" in t:
            r = copy.deepcopy(types[t["extends"]])
            r["name"] = t["name"]
            if "specialize" in t:
                r["fields"] = replace_type(r["fields"], t["specialize"])

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

    for t in n:
        if "fields" in t:
            t["fields"] = replace_type(t["fields"], extended_by)

    n = replace_type(n, ex_types)

    return n

def make_avro_schema(j):
    names = avro.schema.Names()
    j = extend_and_specialize(j)

    j2 = make_valid_avro(j, set())

    j3 = [t for t in j2 if isinstance(t, dict) and not t.get("abstract") and t.get("type") != "doc"]

    # avsc = {
    #     "name": "Container",
    #     "type": "record",
    #     "fields": []
    # }
    # for t in j3:
    #     avsc["fields"].append({
    #         "name": t["name"],
    #         "type": t
    #         })

    avro.schema.make_avsc_object(j3, names)

    return (names, j3)
