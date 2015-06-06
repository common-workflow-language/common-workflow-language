import avro
import copy
from  makedoc import add_dictlist

def specialize(items, spec, extended_by):
    if isinstance(items, dict):
        for n in ("type", "items", "values"):
            if n in items:
                items[n] = specialize(items[n], spec, extended_by)
        return items
    if isinstance(items, list):
        n = []
        for i in items:
            n.append(specialize(i, spec, extended_by))
        return n
    if isinstance(items, basestring):
        if items in spec:
            return spec[items]
        if items in extended_by:
            return extended_by[items]
    return items

def extend_avro(items):
    types = {t["name"]: t for t in items}
    n = []

    extended_by = {}
    for t in items:
        if "extends" in t and types[t["extends"]].get("abstract"):
            add_dictlist(extended_by, t["extends"], t["name"])

    for t in items:
        if "extends" in t:
            r = copy.deepcopy(types[t["extends"]])
            r["name"] = t["name"]
            if "specialize" in t:
                r["fields"] = specialize(r["fields"], t["specialize"], {})

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

    # for t in n:
    #     if "fields" in t:
    #         t["fields"] = specialize(t["fields"], "", extended_by)

    return n

def schema(j):
    names = avro.schema.Names()
    j = extend_avro(j)
    for t in j:
        if not t.get("abstract") and t.get("type") != "doc":
            avro.schema.make_avsc_object(t, names)

    return names
