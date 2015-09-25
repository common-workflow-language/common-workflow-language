import sys
import urlparse

def findId(doc, frg):
    if isinstance(doc, dict):
        if "id" in doc and doc["id"] == frg:
            return doc
        else:
            for d in doc:
                f = findId(doc[d], frg)
                if f:
                    return f
    if isinstance(doc, list):
        for d in doc:
            f = findId(d, frg)
            if f:
                return f
    return None

def fixType(doc):
    if isinstance(doc, list):
        return [fixType(f) for f in doc]

    if isinstance(doc, basestring):
        if doc not in ("null", "boolean", "int", "long", "float", "double", "string", "File", "record", "enum", "array", "Any") and "#" not in doc:
            return "#" + doc
    return doc

def _draft2toDraft3(doc, loader, baseuri):
    if isinstance(doc, dict):
        if "import" in doc:
            imp = urlparse.urljoin(baseuri, doc["import"])
            r = loader.fetch(imp)
            if isinstance(r, list):
                r = {"@graph": r}
            r["id"] = imp
            _, frag = urlparse.urldefrag(imp)
            if frag:
                frag = "#" + frag
                r = findId(r, frag)
            return _draft2toDraft3(r, loader, imp)

        if "include" in doc:
            return loader.fetch_text(urlparse.urljoin(baseuri, doc["include"]))

        for t in ("type", "items"):
            if t in doc:
                doc[t] = fixType(doc[t])

        if "steps" in doc:
            for i, s in enumerate(doc["steps"]):
                if "id" not in s:
                    s["id"] = "step%i" % i
                for inp in s.get("inputs", []):
                    if isinstance(inp.get("source"), list):
                        if "requirements" not in doc:
                            doc["requirements"] = []
                        doc["requirements"].append({"class": "MultipleInputFeatureRequirement"})


        for a in doc:
            doc[a] = _draft2toDraft3(doc[a], loader, baseuri)

    if isinstance(doc, list):
        return [_draft2toDraft3(a, loader, baseuri) for a in doc]

    return doc

def draft2toDraft3(doc, loader, baseuri):
    return (_draft2toDraft3(doc, loader, baseuri), "https://w3id.org/cwl/cwl#draft-3.dev1")

def update(doc, loader, baseuri):
    updates = {
        "https://w3id.org/cwl/cwl#draft-2": draft2toDraft3,
        "https://w3id.org/cwl/cwl#draft-3.dev1": None
    }

    def identity(doc, loader, baseuri):
        v = doc.get("cwlVersion")
        if v:
            return (doc, loader.expand_url(v, ""))
        else:
            return (doc, "https://w3id.org/cwl/cwl#draft-2")

    nextupdate = identity

    while nextupdate:
        (doc, version) = nextupdate(doc, loader, baseuri)
        if version in updates:
            nextupdate = updates[version]
        else:
            raise Exception("Unrecognized version %s" % version)

    doc["cwlVersion"] = version

    return doc
