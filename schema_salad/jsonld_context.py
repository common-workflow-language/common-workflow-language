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
from rdflib import Graph, URIRef
import rdflib.namespace
from rdflib.namespace import RDF, RDFS
import urlparse

def pred(datatype, field, name, context, defaultPrefix, namespaces):
    split = urlparse.urlsplit(name)

    if split.scheme:
        v = name
        (ns, ln) = rdflib.namespace.split_uri(unicode(v))
        name = ln
        #print ns, ln, namespaces
        if ns[0:-1] in namespaces:
            v = namespaces[ns[0:-1]][ln]
    else:
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

def salad_to_jsonld_context(j):
    context = {}
    namespaces = {}
    g = Graph()
    defaultPrefix = ""

    for t in j:
        if "jsonldVocab" in t:
            for prefix in t["jsonldPrefixes"]:
                context[prefix["prefix"]] = prefix["namespace"]
                namespaces[prefix["prefix"]] = rdflib.namespace.Namespace(prefix["namespace"])
        if "jsonldVocab" in t:
            defaultPrefix = t["jsonldVocab"]

    for k,v in namespaces.items():
        g.bind(k, v)

    for t in j:
        if t["type"] == "https://w3id.org/cwl/salad#record":
            recordname = t["name"]

            classnode = namespaces[defaultPrefix][recordname]
            g.add((classnode, RDF.type, RDFS.Class))

            split = urlparse.urlsplit(recordname)
            if "jsonldPrefix" in t:
                predicate = "%s:%s" % (t["jsonldPrefix"], recordname)
            elif split.scheme:
                (ns, ln) = rdflib.namespace.split_uri(unicode(recordname))
                predicate = recordname
                recordname = ln
            else:
                predicate = "%s:%s" % (defaultPrefix, recordname)

            if context.get(recordname, predicate) != predicate:
                raise Exception("Predicate collision on '%s', '%s' != '%s'" % (recordname, context[t["name"]], predicate))

            if not recordname:
                raise Exception()

            context[recordname] = predicate

            for i in t.get("fields", []):
                fieldname = i["name"]

                v = pred(t, i, fieldname, context, defaultPrefix, namespaces)

                #print t, i, fieldname, context, defaultPrefix, v

                if isinstance(v, basestring):
                    v = v if v[0] != "@" else None
                else:
                    v = v["@id"] if v.get("@id", "@")[0] != "@" else None

                if v:
                    (ns, ln) = rdflib.namespace.split_uri(unicode(v))
                    #print ns, ln
                    if ns[0:-1] in namespaces:
                        propnode = namespaces[ns[0:-1]][ln]
                    else:
                        propnode = URIRef(v)

                    g.add((propnode, RDF.type, RDF.Property))
                    g.add((propnode, RDFS.domain, classnode))

                    # TODO generate range from datatype.

            if "extends" in t:
                g.add((classnode, RDFS.subClassOf, namespaces["cwl"][t["extends"]]))
        elif t["type"] == "https://w3id.org/cwl/salad#enum":
            for i in t["symbols"]:
                _, symname = urlparse.urldefrag(i)
                pred(t, None, symname, context, defaultPrefix, namespaces)

    return (context, g)

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        j = yaml.load(f)
        (ctx, g) = salad_to_jsonld_context(j)
        print json.dumps(ctx, indent=4, sort_keys=True)
