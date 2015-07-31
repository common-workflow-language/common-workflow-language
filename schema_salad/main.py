import argparse
import logging
import sys
import pkg_resources  # part of setuptools
import schema
import jsonld_context
import makedoc
import json
from rdflib import Graph, plugin
from rdflib.serializer import Serializer

from ref_resolver import Loader
import validate

_logger = logging.getLogger("salad")
_logger.addHandler(logging.StreamHandler())
_logger.setLevel(logging.INFO)

from rdflib.plugin import register, Parser
import rdflib_jsonld.parser
register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')

def printrdf(workflow, wf, ctx, sr):
    g = Graph().parse(data=json.dumps(wf), format='json-ld', location=workflow, context=ctx)
    print(g.serialize(format=sr))

def create_loader(ctx):
    loader = Loader()
    loader.url_fields = []
    loader.identifiers = []
    for c in ctx:
        if ctx[c] == "@id":
            loader.identifiers.append(c)
        elif isinstance(ctx[c], dict) and ctx[c].get("@type") == "@id":
            loader.url_fields.append(c)
    loader.checked_urls = loader.url_fields
    loader.checked_urls.remove("symbols")
    _logger.debug("url_fields is %s", loader.url_fields)
    return loader


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("--rdf-serializer",
                        help="Output RDF serialization format used by --print-rdf (one of turtle (default), n3, nt, xml)",
                        default="turtle")

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument("--print-jsonld-context", action="store_true", help="Print JSON-LD context for schema")
    exgroup.add_argument("--print-doc", action="store_true", help="Print HTML documentation from schema")
    exgroup.add_argument("--print-rdfs", action="store_true", help="Print RDF schema")
    exgroup.add_argument("--print-avro", action="store_true", help="Print Avro schema")

    exgroup.add_argument("--print-rdf", action="store_true", help="Print corresponding RDF graph for document")
    exgroup.add_argument("--print-pre", action="store_true", help="Print document after preprocessing")
    exgroup.add_argument("--version", action="store_true", help="Print version")

    parser.add_argument("--strict", action="store_true", help="Strict validation (error on unrecognized fields)")

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument("--verbose", action="store_true", help="Default logging")
    exgroup.add_argument("--quiet", action="store_true", help="Only print warnings and errors.")
    exgroup.add_argument("--debug", action="store_true", help="Print even more logging")

    parser.add_argument("schema", type=str)
    parser.add_argument("document", type=str, nargs="?", default=None)

    args = parser.parse_args(args)

    if args.quiet:
        _logger.setLevel(logging.WARN)
    if args.debug:
        _logger.setLevel(logging.DEBUG)

    pkg = pkg_resources.require("schema_salad")
    if pkg:
        if args.version:
            print "%s %s" % (sys.argv[0], pkg[0].version)
            return 0
        else:
            _logger.info("%s %s", sys.argv[0], pkg[0].version)

    (j, names) = schema.get_metaschema()
    (ctx, g) = jsonld_context.salad_to_jsonld_context(j)
    loader = create_loader(ctx)

    if args.print_jsonld_context:
        j = {"@context": ctx}
        print json.dumps(j, indent=4, sort_keys=True)
        return 0

    if args.print_rdfs:
        print(g.serialize(format=args.rdf_serializer))
        return 0

    if args.print_doc:
        makedoc.avrold_doc(j, sys.stdout)
        return 0

    if args.print_avro:
        print "["
        print ", ".join([json.dumps(names.names[n].to_json(), indent=4, sort_keys=True) for n in names.names])
        print "]"
        return 0

    if not args.document:
        parser.print_help()
        _logger.error("")
        _logger.error("Document required")
        return 1

    idx = {}
    try:
        document = loader.resolve_ref(args.document)
    except (validate.ValidationException, RuntimeError) as e:
        _logger.error("Tool definition failed validation:\n%s", e, exc_info=(e if args.debug else False))
        return 1

    if args.print_pre:
        print json.dumps(document, indent=4)
        return 0

    try:
        loader.validate_links(document)
    except (validate.ValidationException) as e:
        _logger.error("Document failed validation:\n%s", e, exc_info=(e if args.debug else False))
        _logger.debug("Index is %s", json.dumps(loader.idx, indent=4))
        return 1

    # Validate

    if args.print_rdf:
        printrdf(args.document, document, ctx, args.rdf_serializer)
        return 0

    print "Document is valid"

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
