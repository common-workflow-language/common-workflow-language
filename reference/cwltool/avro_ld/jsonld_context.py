import shutil
import json
import yaml
import os
import subprocess
import copy
import pprint
import re
import sys
import rdflib
from rdflib import Graph
import rdflib.namespace
from rdflib.namespace import RDF, RDFS

def pred(datatype, field, name, context, defaultPrefix):
    v = None
    if field and "jsonldPredicate" in field:
        v = field["jsonldPredicate"]
    elif "jsonldPredicate" in datatype:
        for d in datatype["jsonldPredicate"]:
            if d["symbol"] == name:
                v = d["predicate"]
    if not v:
        if field and "jsonldPrefix" in field:
            defaultPrefix = field["jsonldPrefix"]
        elif "jsonldPrefix" in datatype:
            defaultPrefix = datatype["jsonldPrefix"]

    if not v:
        v = "%s:%s" % (defaultPrefix, name)

    if name in context:
        if context[name] != v:
            raise Exception("Predicate collision on %s, %s != %s" % (name, context[name], v))
    else:
        context[name] = v

    return v

def avrold_to_jsonld_context(j):
    context = {}
    namespaces = {}
    g = Graph()
    defaultPrefix = ""

    for t in j:
        if "jsonldVocab" in t:
            for prefix in t["jsonldPrefixes"]:
                context[prefix] = t["jsonldPrefixes"][prefix]
                namespaces[prefix] = rdflib.namespace.Namespace(t["jsonldPrefixes"][prefix])
        if "jsonldVocab" in t:
            defaultPrefix = t["jsonldVocab"]

    for k,v in namespaces.items():
        g.bind(k, v)

    for t in j:
        if t["type"] == "record":
            classnode = namespaces["cwl"][t["name"]]
            g.add((classnode, RDF.type, RDFS.Class))

            if "jsonldPrefix" in t:
                predicate = "%s:%s" % (t["jsonldPrefix"], t["name"])
            else:
                predicate = "%s:%s" % (defaultPrefix, t["name"])

            if context.get(t["name"], predicate) != predicate:
                raise Exception("Predicate collision on '%s', '%s' != '%s'" % (t["name"], context[t["name"]], predicate))

            context[t["name"]] = predicate

            for i in t.get("fields", []):
                v = pred(t, i, i["name"], context, defaultPrefix)

                if isinstance(v, basestring):
                    v = v if v[0] != "@" else None
                else:
                    v = v["@id"] if v.get("@id", "@")[0] != "@" else None

                if v:
                    (ns, ln) = rdflib.namespace.split_uri(unicode(v))
                    propnode = namespaces[ns[0:-1]][ln]
                    g.add((propnode, RDF.type, RDF.Property))
                    g.add((propnode, RDFS.domain, classnode))

                    # TODO generate range from datatype.

            if "extends" in t:
                g.add((classnode, RDFS.subClassOf, namespaces["cwl"][t["extends"]]))
        elif t["type"] == "enum":
            for i in t["symbols"]:
                pred(t, None, i, context, defaultPrefix)

    return (context, g)

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        j = yaml.load(f)
        (ctx, g) = avrold_to_jsonld_context(j)
        print json.dumps(ctx, indent=4, sort_keys=True)
