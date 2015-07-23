import avro
import copy
from  makedoc import add_dictlist
import sys
import pprint

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

def first_def(items, found):
    if isinstance(items, dict):
        if "type" in items and items["type"] in ("record", "enum"):
            if items.get("abstract"):
                return items
            if items["name"] in found:
                return items["name"]
            else:
                found.add(items["name"])
        for n in ("type", "items", "values", "fields"):
            if n in items:
                items[n] = first_def(items[n], found)
        return items
    if isinstance(items, list):
        n = []
        for i in items:
            n.append(first_def(i, found))
        return n
    return items

def extend_avro(items):
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

def schema(j):
    names = avro.schema.Names()
    j = extend_avro(j)
    j = first_def(j, set())
    for t in j:
        if isinstance(t, dict) and not t.get("abstract") and t.get("type") != "doc":
            avro.schema.make_avsc_object(t, names)

    return names
