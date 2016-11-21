import collections
import shutil
import json
import ruamel.yaml as yaml
try:
    from ruamel.yaml import CSafeLoader as SafeLoader
except ImportError:
    from ruamel.yaml import SafeLoader  # type: ignore
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
from .aslist import aslist
from typing import Any, cast, Dict, Iterable, Tuple, Union
from .ref_resolver import Loader, ContextType

_logger = logging.getLogger("salad")


def pred(datatype,      # type: Dict[str, Union[Dict, str]]
         field,         # type: Dict
         name,          # type: str
         context,       # type: ContextType
         defaultBase,   # type: str
         namespaces     # type: Dict[str, rdflib.namespace.Namespace]
         ):
    # type: (...) -> Union[Dict, str]
    split = urlparse.urlsplit(name)

    vee = None  # type: Union[str, unicode]

    if split.scheme:
        vee = name
        (ns, ln) = rdflib.namespace.split_uri(unicode(vee))
        name = ln
        if ns[0:-1] in namespaces:
            vee = unicode(namespaces[ns[0:-1]][ln])
        _logger.debug("name, v %s %s", name, vee)

    v = None  # type: Any

    if field and "jsonldPredicate" in field:
        if isinstance(field["jsonldPredicate"], dict):
            v = {}
            for k, val in field["jsonldPredicate"].items():
                v[("@" + k[1:] if k.startswith("_") else k)] = val
            if "@id" not in v:
                v["@id"] = vee
        else:
            v = field["jsonldPredicate"]
    elif "jsonldPredicate" in datatype:
        if isinstance(datatype["jsonldPredicate"], collections.Iterable):
            for d in datatype["jsonldPredicate"]:
                if isinstance(d, dict):
                    if d["symbol"] == name:
                        v = d["predicate"]
                else:
                    raise Exception(
                        "entries in the jsonldPredicate List must be "
                        "Dictionaries")
        else:
            raise Exception("jsonldPredicate must be a List of Dictionaries.")
    # if not v:
    #     if field and "jsonldPrefix" in field:
    #         defaultBase = field["jsonldPrefix"]
    #     elif "jsonldPrefix" in datatype:
    #         defaultBase = datatype["jsonldPrefix"]

    ret = v or vee

    if not ret:
        ret = defaultBase + name

    if name in context:
        if context[name] != ret:
            raise Exception("Predicate collision on %s, '%s' != '%s'" %
                            (name, context[name], ret))
    else:
        _logger.debug("Adding to context '%s' %s (%s)", name, ret, type(ret))
        context[name] = ret

    return ret


def process_type(t,             # type: Dict[str, Any]
                 g,             # type: Graph
                 context,       # type: ContextType
                 defaultBase,   # type: str
                 namespaces,    # type: Dict[str, rdflib.namespace.Namespace]
                 defaultPrefix  # type: str
                 ):
    # type: (...) -> None
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
            raise Exception("Predicate collision on '%s', '%s' != '%s'" % (
                recordname, context[recordname], predicate))

        if not recordname:
            raise Exception()

        _logger.debug("Adding to context '%s' %s (%s)",
                      recordname, predicate, type(predicate))
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
                process_type(i["type"], g, context, defaultBase,
                             namespaces, defaultPrefix)

        if "extends" in t:
            for e in aslist(t["extends"]):
                g.add((classnode, RDFS.subClassOf, URIRef(e)))
    elif t["type"] == "enum":
        _logger.debug("Processing enum %s", t["name"])

        for i in t["symbols"]:
            pred(t, None, i, context, defaultBase, namespaces)


def salad_to_jsonld_context(j, schema_ctx):
    # type: (Iterable, Dict[str, Any]) -> Tuple[ContextType, Graph]
    context = {}  # type: ContextType
    namespaces = {}
    g = Graph()
    defaultPrefix = ""

    for k, v in schema_ctx.items():
        context[k] = v
        namespaces[k] = rdflib.namespace.Namespace(v)

    if "@base" in context:
        defaultBase = cast(str, context["@base"])
        del context["@base"]
    else:
        defaultBase = ""

    for k, v in namespaces.items():
        g.bind(k, v)

    for t in j:
        process_type(t, g, context, defaultBase, namespaces, defaultPrefix)

    return (context, g)


def fix_jsonld_ids(obj,     # type: Union[Dict[unicode, Any], List[Dict[unicode, Any]]]
                   ids      # type: List[unicode]
                   ):
    # type: (...) -> None
    if isinstance(obj, dict):
        for i in ids:
            if i in obj:
                obj["@id"] = obj[i]
        for v in obj.values():
            fix_jsonld_ids(v, ids)
    if isinstance(obj, list):
        for entry in obj:
            fix_jsonld_ids(entry, ids)


def makerdf(workflow,       # type: Union[str, unicode]
            wf,             # type: Union[List[Dict[unicode, Any]], Dict[unicode, Any]]
            ctx,            # type: ContextType
            graph=None      # type: Graph
            ):
    # type: (...) -> Graph
    prefixes = {}
    idfields = []
    for k, v in ctx.iteritems():
        if isinstance(v, dict):
            url = v["@id"]
        else:
            url = v
        if url == "@id":
            idfields.append(k)
        doc_url, frg = urlparse.urldefrag(url)
        if "/" in frg:
            p = frg.split("/")[0]
            prefixes[p] = u"%s#%s/" % (doc_url, p)

    fix_jsonld_ids(wf, idfields)

    if graph is None:
        g = Graph()
    else:
        g = graph

    if isinstance(wf, list):
        for w in wf:
            w["@context"] = ctx
            g.parse(data=json.dumps(w), format='json-ld', location=workflow)
    else:
        wf["@context"] = ctx
        g.parse(data=json.dumps(wf), format='json-ld', location=workflow)

    # Bug in json-ld loader causes @id fields to be added to the graph
    for sub, pred, obj in g.triples((None, URIRef("@id"), None)):
        g.remove((sub, pred, obj))

    for k2, v2 in prefixes.iteritems():
        g.namespace_manager.bind(k2, v2)

    return g
