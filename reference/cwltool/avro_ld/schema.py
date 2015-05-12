import avro
import copy

def specialize(items, spec):
    if isinstance(items, dict):
        for n in ("type", "items", "values"):
            if n in items:
                items[n] = specialize(items[n], spec)
        return items
    if isinstance(items, list):
        n = []
        for i in items:
            n.append(specialize(i, spec))
        return n
    if isinstance(items, basestring):
        if items in spec:
            return spec[items]
    return items

def extend_avro(items):
    types = {t["name"]: t for t in items}
    n = []
    for t in items:
        if "extends" in t:
            r = copy.deepcopy(types[t["extends"]])
            r["name"] = t["name"]
            if "specialize" in t:
                r["fields"] = specialize(r["fields"], t["specialize"])
            r["fields"].extend(t["fields"])
            r["extends"] = t["extends"]
            r["abstract"] = t.get("abstract", False)
            r["doc"] = t.get("doc", "")
            types[t["name"]] = r
            t = r
        n.append(t)
    return n

def schema(j):
    names = avro.schema.Names()
    j = extend_avro(j)
    for t in j:
        if not t.get("abstract"):
            avro.schema.make_avsc_object(t, names)
    return names
