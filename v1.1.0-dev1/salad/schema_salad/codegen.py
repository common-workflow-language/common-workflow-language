import json
import sys
from six.moves import urllib, cStringIO
import collections
import logging
from pkg_resources import resource_stream
from .utils import aslist, flatten
from . import schema
from .codegen_base import shortname, CodeGenBase
from .python_codegen import PythonCodeGen
from .java_codegen import JavaCodeGen
from .ref_resolver import Loader
from typing import List, Dict, Text, Any, Union, Text
from ruamel.yaml.comments import CommentedSeq, CommentedMap

class GoCodeGen(object):
    pass


def codegen(lang,             # type: str
            i,                # type: List[Dict[Text, Any]]
            schema_metadata,  # type: Dict[Text, Any]
            loader            # type: Loader
           ):
    # type: (...) -> None

    j = schema.extend_and_specialize(i, loader)

    cg = None  # type: CodeGenBase
    if lang == "python":
        cg = PythonCodeGen(sys.stdout)
    elif lang == "java":
        cg = JavaCodeGen(schema_metadata.get("$base", schema_metadata.get("id")))
    else:
        raise Exception("Unsupported code generation language '%s'" % lang)

    cg.prologue()

    documentRoots = []

    for rec in j:
        if rec["type"] in ("enum", "record"):
            cg.type_loader(rec)
            cg.add_vocab(shortname(rec["name"]), rec["name"])

    for rec in j:
        if rec["type"] == "enum":
            for s in rec["symbols"]:
                cg.add_vocab(shortname(s), s)

        if rec["type"] == "record":
            if rec.get("documentRoot"):
                documentRoots.append(rec["name"])
            cg.begin_class(rec["name"], aslist(rec.get("extends", [])), rec.get("doc"),
                           rec.get("abstract"))
            cg.add_vocab(shortname(rec["name"]), rec["name"])

            for f in rec.get("fields", []):
                if f.get("jsonldPredicate") == "@id":
                    fieldpred = f["name"]
                    tl = cg.uri_loader(cg.type_loader(f["type"]), True, False, None)
                    cg.declare_id_field(fieldpred, tl, f.get("doc"))
                    break

            for f in rec.get("fields", []):
                optional = bool("https://w3id.org/cwl/salad#null" in f["type"])
                tl = cg.type_loader(f["type"])
                jld = f.get("jsonldPredicate")
                fieldpred = f["name"]
                if isinstance(jld, dict):
                    refScope = jld.get("refScope")

                    if jld.get("typeDSL"):
                        tl = cg.typedsl_loader(tl, refScope)
                    elif jld.get("_type") == "@id":
                        tl = cg.uri_loader(tl, jld.get("identity"), False, refScope)
                    elif jld.get("_type") == "@vocab":
                        tl = cg.uri_loader(tl, False, True, refScope)

                    mapSubject = jld.get("mapSubject")
                    if mapSubject:
                        tl = cg.idmap_loader(f["name"], tl, mapSubject, jld.get("mapPredicate"))

                    if "_id" in jld and jld["_id"][0] != "@":
                        fieldpred = jld["_id"]

                if jld == "@id":
                    continue

                cg.declare_field(fieldpred, tl, f.get("doc"), optional)

            cg.end_class(rec["name"])

    rootType = list(documentRoots)
    rootType.append({
        "type": "array",
        "items": documentRoots
    })

    cg.epilogue(cg.type_loader(rootType))
