from __future__ import print_function
from __future__ import absolute_import
import argparse
import logging
import sys
import traceback
import json
import os
import re
import itertools

import six
from six.moves import urllib

import pkg_resources  # part of setuptools

from typing import Any, Dict, List, Union, Pattern, Text, Tuple, cast

from rdflib import Graph, plugin
from rdflib.serializer import Serializer

from . import schema
from . import jsonld_context
from . import makedoc
from . import validate
from . import codegen
from .sourceline import strip_dup_lineno
from .ref_resolver import Loader, file_uri
_logger = logging.getLogger("salad")

from rdflib.plugin import register, Parser
register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')


def printrdf(workflow,  # type: str
             wf,        # type: Union[List[Dict[Text, Any]], Dict[Text, Any]]
             ctx,       # type: Dict[Text, Any]
             sr         # type: str
             ):
    # type: (...) -> None
    g = jsonld_context.makerdf(workflow, wf, ctx)
    print(g.serialize(format=sr, encoding='utf-8').decode('utf-8'))

def regex_chunk(lines, regex):
    # type: (List[str], Pattern[str]) -> List[List[str]]
    lst = list(itertools.dropwhile(lambda x: not regex.match(x), lines))
    arr = []
    while lst:
        ret = [lst[0]]+list(itertools.takewhile(lambda x: not regex.match(x),
                                                lst[1:]))
        arr.append(ret)
        lst = list(itertools.dropwhile(lambda x: not regex.match(x),
                                       lst[1:]))
    return arr


def chunk_messages(message):  # type: (str) -> List[Tuple[int, str]]
    file_regex = re.compile(r'^(.+:\d+:\d+:)(\s+)(.+)$')
    item_regex = re.compile(r'^\s*\*\s+')
    arr = []
    for chun in regex_chunk(message.splitlines(), file_regex):
        fst = chun[0]
        mat = file_regex.match(fst)
        place = mat.group(1)
        indent = len(mat.group(2))

        lst = [mat.group(3)]+chun[1:]
        if [x for x in lst if item_regex.match(x)]:
            for item in regex_chunk(lst, item_regex):
                msg = re.sub(item_regex, '', "\n".join(item))
                arr.append((indent, place+' '+re.sub(r'[\n\s]+',
                                                     ' ',
                                                     msg)))
        else:
            msg = re.sub(item_regex, '', "\n".join(lst))
            arr.append((indent, place+' '+re.sub(r'[\n\s]+',
                                                 ' ',
                                                 msg)))
    return arr


def to_one_line_messages(message):  # type: (str) -> str
    ret = []
    max_elem = (0, '')
    for (indent, msg) in chunk_messages(message):
        if indent > max_elem[0]:
            max_elem = (indent, msg)
        else:
            ret.append(max_elem[1])
            max_elem = (indent, msg)
    ret.append(max_elem[1])
    return "\n".join(ret)


def reformat_yaml_exception_message(message):  # type: (str) -> str
    line_regex = re.compile(r'^\s+in "(.+)", line (\d+), column (\d+)$')
    fname_regex = re.compile(r'^file://'+os.getcwd()+'/')
    msgs = message.splitlines()
    ret = []

    if len(msgs) == 3:
        msgs = msgs[1:]
        nblanks = 0
    elif len(msgs) == 4:
        c_msg = msgs[0]
        c_file, c_line, c_column = line_regex.match(msgs[1]).groups()
        c_file = re.sub(fname_regex, '', c_file)
        ret.append("%s:%s:%s: %s" % (c_file, c_line, c_column, c_msg))

        msgs = msgs[2:]
        nblanks = 2

    p_msg = msgs[0]
    p_file, p_line, p_column = line_regex.match(msgs[1]).groups()
    p_file = re.sub(fname_regex, '', p_file)
    ret.append("%s:%s:%s:%s %s" % (p_file, p_line, p_column, ' '*nblanks, p_msg))
    return "\n".join(ret)


def main(argsl=None):  # type: (List[str]) -> int
    if argsl is None:
        argsl = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("--rdf-serializer",
                        help="Output RDF serialization format used by --print-rdf (one of turtle (default), n3, nt, xml)",
                        default="turtle")

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument("--print-jsonld-context", action="store_true",
                         help="Print JSON-LD context for schema")
    exgroup.add_argument(
        "--print-rdfs", action="store_true", help="Print RDF schema")
    exgroup.add_argument("--print-avro", action="store_true",
                         help="Print Avro schema")

    exgroup.add_argument("--print-rdf", action="store_true",
                         help="Print corresponding RDF graph for document")
    exgroup.add_argument("--print-pre", action="store_true",
                         help="Print document after preprocessing")
    exgroup.add_argument(
        "--print-index", action="store_true", help="Print node index")
    exgroup.add_argument("--print-metadata",
                         action="store_true", help="Print document metadata")
    exgroup.add_argument("--print-inheritance-dot",
                         action="store_true", help="Print graphviz file of inheritance")
    exgroup.add_argument("--print-fieldrefs-dot",
                         action="store_true", help="Print graphviz file of field refs")

    exgroup.add_argument("--codegen", type=str, metavar="language", help="Generate classes in target language, currently supported: python")

    exgroup.add_argument("--print-oneline", action="store_true",
                         help="Print each error message in oneline")

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument("--strict", action="store_true", help="Strict validation (unrecognized or out of place fields are error)",
                         default=True, dest="strict")
    exgroup.add_argument("--non-strict", action="store_false", help="Lenient validation (ignore unrecognized fields)",
                         default=True, dest="strict")

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument("--verbose", action="store_true",
                         help="Default logging")
    exgroup.add_argument("--quiet", action="store_true",
                         help="Only print warnings and errors.")
    exgroup.add_argument("--debug", action="store_true",
                         help="Print even more logging")

    parser.add_argument("schema", type=str, nargs="?", default=None)
    parser.add_argument("document", type=str, nargs="?", default=None)
    parser.add_argument("--version", "-v", action="store_true",
                        help="Print version", default=None)


    args = parser.parse_args(argsl)

    if args.version is None and args.schema is None:
        print('%s: error: too few arguments' % sys.argv[0])
        return 1

    if args.quiet:
        _logger.setLevel(logging.WARN)
    if args.debug:
        _logger.setLevel(logging.DEBUG)

    pkg = pkg_resources.require("schema_salad")
    if pkg:
        if args.version:
            print("%s Current version: %s" % (sys.argv[0], pkg[0].version))
            return 0
        else:
            _logger.info("%s Current version: %s", sys.argv[0], pkg[0].version)

    # Get the metaschema to validate the schema
    metaschema_names, metaschema_doc, metaschema_loader = schema.get_metaschema()

    # Load schema document and resolve refs

    schema_uri = args.schema
    if not (urllib.parse.urlparse(schema_uri)[0] and urllib.parse.urlparse(schema_uri)[0] in [u'http', u'https', u'file']):
        schema_uri = file_uri(os.path.abspath(schema_uri))
    schema_raw_doc = metaschema_loader.fetch(schema_uri)

    try:
        schema_doc, schema_metadata = metaschema_loader.resolve_all(
            schema_raw_doc, schema_uri)
    except (validate.ValidationException) as e:
        _logger.error("Schema `%s` failed link checking:\n%s",
                      args.schema, e, exc_info=(True if args.debug else False))
        _logger.debug("Index is %s", list(metaschema_loader.idx.keys()))
        _logger.debug("Vocabulary is %s", list(metaschema_loader.vocab.keys()))
        return 1
    except (RuntimeError) as e:
        _logger.error("Schema `%s` read error:\n%s",
                      args.schema, e, exc_info=(True if args.debug else False))
        return 1

    # Optionally print the schema after ref resolution
    if not args.document and args.print_pre:
        print(json.dumps(schema_doc, indent=4))
        return 0

    if not args.document and args.print_index:
        print(json.dumps(list(metaschema_loader.idx.keys()), indent=4))
        return 0

    # Validate the schema document against the metaschema
    try:
        schema.validate_doc(metaschema_names, schema_doc,
                            metaschema_loader, args.strict,
                            source=schema_metadata.get("name"))
    except validate.ValidationException as e:
        _logger.error("While validating schema `%s`:\n%s" %
                      (args.schema, str(e)))
        return 1

    # Get the json-ld context and RDFS representation from the schema
    metactx = {}  # type: Dict[str, str]
    if isinstance(schema_raw_doc, dict):
        metactx = schema_raw_doc.get("$namespaces", {})
        if "$base" in schema_raw_doc:
            metactx["@base"] = schema_raw_doc["$base"]
    if schema_doc is not None:
        (schema_ctx, rdfs) = jsonld_context.salad_to_jsonld_context(
            schema_doc, metactx)
    else:
        raise Exception("schema_doc is None??")

    # Create the loader that will be used to load the target document.
    document_loader = Loader(schema_ctx)

    if args.codegen:
        codegen.codegen(args.codegen, cast(List[Dict[Text, Any]], schema_doc),
                        schema_metadata, document_loader)
        return 0

    # Make the Avro validation that will be used to validate the target
    # document
    if isinstance(schema_doc, list):
        (avsc_names, avsc_obj) = schema.make_avro_schema(
            schema_doc, document_loader)
    else:
        _logger.error("Schema `%s` must be a list.", args.schema)
        return 1

    if isinstance(avsc_names, Exception):
        _logger.error("Schema `%s` error:\n%s", args.schema,
                      avsc_names, exc_info=((type(avsc_names), avsc_names,
                                             None) if args.debug else None))
        if args.print_avro:
            print(json.dumps(avsc_obj, indent=4))
        return 1

    # Optionally print Avro-compatible schema from schema
    if args.print_avro:
        print(json.dumps(avsc_obj, indent=4))
        return 0

    # Optionally print the json-ld context from the schema
    if args.print_jsonld_context:
        j = {"@context": schema_ctx}
        print(json.dumps(j, indent=4, sort_keys=True))
        return 0

    # Optionally print the RDFS graph from the schema
    if args.print_rdfs:
        print(rdfs.serialize(format=args.rdf_serializer))
        return 0

    if args.print_metadata and not args.document:
        print(json.dumps(schema_metadata, indent=4))
        return 0

    if args.print_inheritance_dot:
        schema.print_inheritance(schema_doc, sys.stdout)
        return 0

    if args.print_fieldrefs_dot:
        schema.print_fieldrefs(schema_doc, document_loader, sys.stdout)
        return 0

    # If no document specified, all done.
    if not args.document:
        print("Schema `%s` is valid" % args.schema)
        return 0

    # Load target document and resolve refs
    try:
        uri = args.document
        if not urllib.parse.urlparse(uri)[0]:
            doc = "file://" + os.path.abspath(uri)
        document, doc_metadata = document_loader.resolve_ref(uri)
    except validate.ValidationException as e:
        msg = strip_dup_lineno(six.text_type(e))
        msg = to_one_line_messages(str(msg)) if args.print_oneline else msg
        _logger.error("Document `%s` failed validation:\n%s",
                      args.document, msg, exc_info=args.debug)
        return 1
    except RuntimeError as e:
        msg = strip_dup_lineno(six.text_type(e))
        msg = reformat_yaml_exception_message(str(msg))
        msg = to_one_line_messages(msg) if args.print_oneline else msg
        _logger.error("Document `%s` failed validation:\n%s",
                      args.document, msg, exc_info=args.debug)
        return 1

    # Optionally print the document after ref resolution
    if args.print_pre:
        print(json.dumps(document, indent=4))
        return 0

    if args.print_index:
        print(json.dumps(list(document_loader.idx.keys()), indent=4))
        return 0

    # Validate the schema document against the metaschema
    try:
        schema.validate_doc(avsc_names, document,
                            document_loader, args.strict)
    except validate.ValidationException as e:
        msg = to_one_line_messages(str(e)) if args.print_oneline else str(e)
        _logger.error("While validating document `%s`:\n%s" %
                      (args.document, msg))
        return 1

    # Optionally convert the document to RDF
    if args.print_rdf:
        if isinstance(document, (dict, list)):
            printrdf(args.document, document, schema_ctx, args.rdf_serializer)
            return 0
        else:
            print("Document must be a dictionary or list.")
            return 1

    if args.print_metadata:
        print(json.dumps(doc_metadata, indent=4))
        return 0

    print("Document `%s` is valid" % args.document)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
