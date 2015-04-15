#!/usr/bin/env python

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

module_dir = os.path.dirname(os.path.abspath(__file__))
cwl_avsc = os.path.join(module_dir, '../../schemas/draft-2/cwl-avro.yml')

context = {
    "cwl": "http://github.com/common-workflow-language#",
    "avro": "http://github.com/common-workflow-language#avro/",
    "wfdesc": "http://purl.org/wf4ever/wfdesc#",
    "dct": "http://purl.org/dc/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
}

g = Graph()

namespaces = {
    "cwl": rdflib.namespace.Namespace('http://github.com/common-workflow-language#'),
    "avro": rdflib.namespace.Namespace("http://github.com/common-workflow-language#avro/"),
    "wfdesc": rdflib.namespace.Namespace("http://purl.org/wf4ever/wfdesc#"),
    "dct": rdflib.namespace.DCTERMS,
    "rdf": rdflib.namespace.RDF,
    "rdfs": rdflib.namespace.RDFS
}

for k,v in namespaces.items():
    g.bind(k, v)

def pred(datatype, field, name):
    v = None
    if field and "jsonldPredicate" in field:
        v = field["jsonldPredicate"]
    elif field and "jsonldPrefix" in field:
        v = "%s:%s" % (field["jsonldPrefix"], name)
    elif "jsonldPrefix" in datatype:
        v = "%s:%s" % (datatype["jsonldPrefix"], name)
    else:
        v = "cwl:%s" % (name)
    if v:
        if name in context:
            if context[name] != v:
                raise Exception("Predicate collision on %s, %s != %s" % (name, context[name], v))
        else:
            context[name] = v

    return v

with open(cwl_avsc) as f:
    j = yaml.load(f)

for t in j:
    if t["type"] == "record":
        classnode = namespaces["cwl"][t["name"]]
        g.add((classnode, RDF.type, RDFS.Class))

        if t["name"] in context:
            raise Exception("Collision on %s" % t["name"])

        if "jsonldPrefix" in t:
            context[t["name"]] = "%s:%s" % (t["jsonldPrefix"], t["name"])
        else:
            context[t["name"]] = "cwl:%s" % (t["name"])

        for i in t["fields"]:
            v = pred(t, i, i["name"])

            if isinstance(v, basestring):
                v = v if v[0] != "@" else None
            else:
                v = v["@id"] if v["@id"][0] != "@" else None

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
            pred(t, None, i)

print json.dumps(context, indent=4, sort_keys=True)

print g.serialize(format='turtle')
