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
    for c in ctx:
        if ctx[c] == "@id":
            loader.identifiers.append(c)
        elif isinstance(ctx[c], dict) and ctx[c].get("@type") == "@id":
            loader.url_fields.append(c)
            if ctx[c].get("checkedURI", True):
                loader.checked_urls(c)
        elif isinstance(ctx[c], dict) and ctx[c].get("@type") == "@vocab":
            loader.url_fields.append(c)
            loader.vocab_fields.append(c)

        if isinstance(ctx[c], dict) and "@id" in ctx[c]:
            loader.vocab[c] = ctx[c]["@id"]
        elif isinstance(ctx[c], basestring):
            loader.vocab[c] = ctx[c]

    _logger.debug("identifiers is %s", loader.identifiers)
    _logger.debug("url_fields is %s", loader.url_fields)
    _logger.debug("checked_urls is %s", loader.checked_urls)
    _logger.debug("vocab_fields is %s", loader.vocab_fields)
    _logger.debug("vocab is %s", loader.vocab)


    return loader

def validate_doc(schema_names, validate_doc, strict):
    for item in validate_doc:
        for r in schema_names.names.values():
            if r.get_prop("validationRoot"):
                errors = []
                try:
                    validate.validate_ex(r, item, strict)
                    break
                except validate.ValidationException as e:
                    errors.append(str(e))
                _logger.error("Document failed validation:\n%s", "\n".join(errors))
                return False
    return True


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

    # Get the metaschema to validate the schema
    metaschema_names, metaschema_doc, metaschema_loader = schema.get_metaschema()

    # Load schema document and resolve refs
    schema_doc = metaschema_loader.resolve_ref("file://" + os.path.abspath(args.schema))

    # Optionally print the schema after ref resolution
    if not args.document and args.print_pre:
        print json.dumps(schema_doc, indent=4)
        return 0

    # Validate links in the schema document
    try:
        metaschema_loader.validate_links(schema_doc)
    except (validate.ValidationException) as e:
        _logger.error("Document failed validation:\n%s", e, exc_info=(e if args.debug else False))
        #_logger.debug("Index is %s", json.dumps(loader.idx, indent=4))
        return 1

    # Validate the schema document against the metaschema
    try:
        validate_doc(metaschema_names, schema_doc, args.strict)
    except Exception as e:
        _logger.error(e)
        return 1

    # Get the json-ld context and RDFS representation from the schema
    (schema_ctx, rdfs) = jsonld_context.salad_to_jsonld_context(schema_doc)

    # Create the loader that will be used to load the target document.
    document_loader = create_loader(schema_ctx)

    # Make the Avro validation that will be used to validate the target document
    (avsc_names, avsc_obj) = schema.make_avro_schema(schema_doc)

    # Optionally print the json-ld context from the schema
    if args.print_jsonld_context:
        j = {"@context": schema_ctx}
        print json.dumps(j, indent=4, sort_keys=True)
        return 0

    # Optionally print the RDFS graph from the schema
    if args.print_rdfs:
        print(g.serialize(format=args.rdf_serializer))
        return 0

    # Optionally create documentation page from the schema
    if args.print_doc:
        makedoc.avrold_doc(schema_doc, sys.stdout)
        return 0

    # Optionally print Avro-compatible schema from schema
    if args.print_avro:
        print json.dumps(avsc_obj, indent=4)
        return 0

    # If no document specified, all done.
    if not args.document:
        print "Schema is valid"
        return 0

    # Load target document and resolve refs
    try:
        document = document_loader.resolve_ref("file://" + os.path.abspath(args.document))
    except (validate.ValidationException, RuntimeError) as e:
        _logger.error("Tool definition failed validation:\n%s", e, exc_info=(e if args.debug else False))
        return 1

    # Optionally print the document after ref resolution
    if args.print_pre:
        print json.dumps(document, indent=4)
        return 0

    # Validate links in the target document
    try:
        document_loader.validate_links(document)
    except (validate.ValidationException) as e:
        _logger.error("Document failed validation:\n%s", e, exc_info=(e if args.debug else False))
        #_logger.debug("Index is %s", json.dumps(loader.idx, indent=4))
        return 1

    # Validate the schema document against the metaschema
    try:
        validate_doc(avsc_names, document, args.strict)
    except Exception as e:
        _logger.error(e)
        return 1

    # Optionally convert the document to RDF
    if args.print_rdf:
        printrdf(args.document, document, ctx, args.rdf_serializer)
        return 0

    print "Document is valid"

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
