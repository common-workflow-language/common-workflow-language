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
import logging
from aslist import aslist

_logger = logging.getLogger("salad")

def pred(datatype, field, name, context, defaultBase, namespaces):
    split = urlparse.urlsplit(name)

    v = None

    if split.scheme:
        v = name
        (ns, ln) = rdflib.namespace.split_uri(unicode(v))
        name = ln
        if ns[0:-1] in namespaces:
            v = unicode(namespaces[ns[0:-1]][ln])
        _logger.debug("name, v %s %s", name, v)

    if field and "jsonldPredicate" in field:
        if isinstance(field["jsonldPredicate"], dict):
            v = {("@"+k[1:] if k.startswith("_") else k): v
                 for k,v in field["jsonldPredicate"].items() }
        else:
            v = field["jsonldPredicate"]
    elif "jsonldPredicate" in datatype:
        for d in datatype["jsonldPredicate"]:
            if d["symbol"] == name:
                v = d["predicate"]
    # if not v:
    #     if field and "jsonldPrefix" in field:
    #         defaultBase = field["jsonldPrefix"]
    #     elif "jsonldPrefix" in datatype:
    #         defaultBase = datatype["jsonldPrefix"]

    if not v:
        v = defaultBase + name

    if name in context:
        if context[name] != v:
            raise Exception("Predicate collision on %s, '%s' != '%s'" % (name, context[name], v))
    else:
        _logger.debug("Adding to context '%s' %s (%s)", name, v, type(v))
        context[name] = v

    return v

def process_type(t, g, context, defaultBase, namespaces, defaultPrefix):
    if t["type"] == "record":
        recordname = t["name"]

        _logger.debug("Processing record %s\n", t)

        classnode = URIRef(recordname)
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

        _logger.debug("Adding to context '%s' %s (%s)", recordname, predicate, type(predicate))
        context[recordname] = predicate

        for i in t.get("fields", []):
            fieldname = i["name"]

            _logger.debug("Processing field %s", i)

            v = pred(t, i, fieldname, context, defaultPrefix, namespaces)

            if isinstance(v, basestring):
                v = v if v[0] != "@" else None
            else:
                v = v["_@id"] if v.get("_@id", "@")[0] != "@" else None

            if v:
                (ns, ln) = rdflib.namespace.split_uri(unicode(v))
                if ns[0:-1] in namespaces:
                    propnode = namespaces[ns[0:-1]][ln]
                else:
                    propnode = URIRef(v)

                g.add((propnode, RDF.type, RDF.Property))
                g.add((propnode, RDFS.domain, classnode))

                # TODO generate range from datatype.

            if isinstance(i["type"], dict) and "name" in i["type"]:
                process_type(i["type"], g, context, defaultBase, namespaces, defaultPrefix)

        if "extends" in t:
            for e in aslist(t["extends"]):
                g.add((classnode, RDFS.subClassOf, URIRef(e)))
    elif t["type"] == "enum":
        _logger.debug("Processing enum %s", t["name"])

        for i in t["symbols"]:
            pred(t, None, i, context, defaultBase, namespaces)


def salad_to_jsonld_context(j, schema_ctx):
    context = {}
    namespaces = {}
    g = Graph()
    defaultPrefix = ""

    for k,v in schema_ctx.items():
        context[k] = v
        namespaces[k] = rdflib.namespace.Namespace(v)

    if "@base" in context:
        defaultBase = context["@base"]
        del context["@base"]
    else:
        defaultBase = ""

    for k,v in namespaces.items():
        g.bind(k, v)

    for t in j:
        process_type(t, g, context, defaultBase, namespaces, defaultPrefix)

    return (context, g)

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        j = yaml.load(f)
        (ctx, g) = salad_to_jsonld_context(j)
        print json.dumps(ctx, indent=4, sort_keys=True)
