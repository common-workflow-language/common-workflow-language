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
import yaml
import os
import urlparse

from ref_resolver import Loader
import validate

_logger = logging.getLogger("salad")

from rdflib.plugin import register, Parser
import rdflib_jsonld.parser
register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')

def printrdf(workflow, wf, ctx, sr):
    g = Graph().parse(data=json.dumps(wf), format='json-ld', location=workflow, context=ctx)
    print(g.serialize(format=sr))

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
    exgroup.add_argument("--print-index", action="store_true", help="Print node index")
    exgroup.add_argument("--print-metadata", action="store_true", help="Print document metadata")
    exgroup.add_argument("--version", action="store_true", help="Print version")

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument("--strict", action="store_true", help="Strict validation (unrecognized or out of place fields are error)",
                         default=True, dest="strict")
    exgroup.add_argument("--non-strict", action="store_false", help="Lenient validation (ignore unrecognized fields)",
                         default=True, dest="strict")

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

    # Get the metaschema to validate the schema
    metaschema_names, metaschema_doc, metaschema_loader = schema.get_metaschema()

    # Load schema document and resolve refs

    schema_uri = args.schema
    if not urlparse.urlparse(schema_uri)[0]:
        schema_uri = "file://" + os.path.abspath(schema_uri)
    schema_raw_doc = metaschema_loader.fetch(schema_uri)
    schema_doc, schema_metadata = metaschema_loader.resolve_all(schema_raw_doc, schema_uri)

    # Optionally print the schema after ref resolution
    if not args.document and args.print_pre:
        print json.dumps(schema_doc, indent=4)
        return 0

    if not args.document and args.print_index:
        print json.dumps(metaschema_loader.idx.keys(), indent=4)
        return 0

    # Validate links in the schema document
    try:
        metaschema_loader.validate_links(schema_doc)
    except (validate.ValidationException) as e:
        _logger.error("Schema `%s` failed link checking:\n%s", args.schema, e, exc_info=(e if args.debug else False))
        _logger.debug("Index is %s", metaschema_loader.idx.keys())
        _logger.debug("Vocabulary is %s", metaschema_loader.vocab.keys())
        return 1

    # Validate the schema document against the metaschema
    try:
        schema.validate_doc(metaschema_names, schema_doc, metaschema_loader, args.strict)
    except validate.ValidationException as e:
        _logger.error("While validating schema `%s`:\n%s" % (args.schema, str(e)))
        return 1

    # Get the json-ld context and RDFS representation from the schema
    metactx = {}
    if isinstance(schema_raw_doc, dict):
        metactx = schema_raw_doc.get("$namespaces", {})
        if "$base" in schema_raw_doc:
            metactx["@base"] = schema_raw_doc["$base"]
    (schema_ctx, rdfs) = jsonld_context.salad_to_jsonld_context(schema_doc, metactx)

    # Create the loader that will be used to load the target document.
    document_loader = Loader(schema_ctx)

    # Make the Avro validation that will be used to validate the target document
    (avsc_names, avsc_obj) = schema.make_avro_schema(schema_doc, document_loader)

    if isinstance(avsc_names, Exception):
        _logger.error("Schema `%s` error:\n%s", args.schema, avsc_names, exc_info=(avsc_names if args.debug else False))
        if args.print_avro:
            print json.dumps(avsc_obj, indent=4)
        return 1

    # Optionally print Avro-compatible schema from schema
    if args.print_avro:
        print json.dumps(avsc_obj, indent=4)
        return 0

    # Optionally print the json-ld context from the schema
    if args.print_jsonld_context:
        j = {"@context": schema_ctx}
        print json.dumps(j, indent=4, sort_keys=True)
        return 0

    # Optionally print the RDFS graph from the schema
    if args.print_rdfs:
        print(rdfs.serialize(format=args.rdf_serializer))
        return 0

    # Optionally create documentation page from the schema
    if args.print_doc:
        makedoc.avrold_doc(schema_doc, sys.stdout)
        return 0

    if args.print_metadata and not args.document:
        print json.dumps(schema_metadata, indent=4)
        return 0

    # If no document specified, all done.
    if not args.document:
        print "Schema `%s` is valid" % args.schema
        return 0

    # Load target document and resolve refs
    try:
        uri = args.document
        if not urlparse.urlparse(uri)[0]:
            doc = "file://" + os.path.abspath(uri)
        document, doc_metadata = document_loader.resolve_ref(uri)
    except (validate.ValidationException, RuntimeError) as e:
        _logger.error("Document `%s` failed validation:\n%s", args.document, e, exc_info=(e if args.debug else False))
        return 1

    # Optionally print the document after ref resolution
    if args.print_pre:
        print json.dumps(document, indent=4)
        return 0

    if args.print_index:
        print json.dumps(document_loader.idx.keys(), indent=4)
        return 0

    # Validate links in the target document
    try:
        document_loader.validate_links(document)
    except (validate.ValidationException) as e:
        _logger.error("Document `%s` failed link checking:\n%s", args.document, e, exc_info=(e if args.debug else False))
        _logger.debug("Index is %s", json.dumps(document_loader.idx.keys(), indent=4))
        return 1

    # Validate the schema document against the metaschema
    try:
        schema.validate_doc(avsc_names, document, document_loader, args.strict)
    except validate.ValidationException as e:
        _logger.error("While validating document `%s`:\n%s" % (args.document, str(e)))
        return 1

    # Optionally convert the document to RDF
    if args.print_rdf:
        printrdf(args.document, document, schema_ctx, args.rdf_serializer)
        return 0

    if args.print_metadata:
        print json.dumps(doc_metadata, indent=4)
        return 0

    print "Document `%s` is valid" % args.document

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
