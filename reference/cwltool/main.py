#!/usr/bin/env python

import draft1tool
import draft2tool
import argparse
from ref_resolver import from_url, validate_links
import jsonschema
import json
import os
import sys
import logging
import workflow
import avro_ld.validate as validate
import tempfile
import avro_ld.jsonld_context
import avro_ld.makedoc
import yaml

_logger = logging.getLogger("cwltool")
_logger.addHandler(logging.StreamHandler())

module_dir = os.path.dirname(os.path.abspath(__file__))

def printrdf(workflow, wf, ctx, sr):
    from rdflib import Graph, plugin
    from rdflib.serializer import Serializer
    wf["@context"] = ctx
    g = Graph().parse(data=json.dumps(wf), format='json-ld', location=workflow)
    print(g.serialize(format=sr))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=str, nargs="?", default=None)
    parser.add_argument("job_order", type=str, nargs="?", default=None)
    parser.add_argument("--conformance-test", action="store_true")
    parser.add_argument("--basedir", type=str)
    parser.add_argument("--outdir", type=str)
    parser.add_argument("--no-container", action="store_true", help="Do not execute jobs in a Docker container, even when specified by the CommandLineTool")
    parser.add_argument("--leave-container", action="store_true", help="Do not delete Docker container used by jobs after they exit")
    parser.add_argument("--no-pull", default=False, action="store_true", help="Do not try to pull Docker images")
    parser.add_argument("--dry-run", action="store_true", help="Load and validate but do not execute")

    parser.add_argument("--print-rdf", action="store_true", help="Print corresponding RDF graph for workflow")
    parser.add_argument("--rdf-serializer", help="Output RDF serialization format (one of turtle (default), n3, nt, xml)", default="turtle")

    parser.add_argument("--print-spec", action="store_true", help="Print HTML specification document")
    parser.add_argument("--print-jsonld-context", action="store_true", help="Print JSON-LD context for CWL file")
    parser.add_argument("--print-rdfs", action="store_true", help="Print JSON-LD context for CWL file")
    parser.add_argument("--print-avro", action="store_true", help="Print Avro schema")
    parser.add_argument("--print-pre", action="store_true", help="Print workflow document after preprocessing")
    parser.add_argument("--strict", action="store_true", help="Strict validation (unrecognized fields are an error) (default false)")

    parser.add_argument("--verbose", action="store_true", help="Print more logging")
    parser.add_argument("--debug", action="store_true", help="Print even more logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger("cwltool").setLevel(logging.INFO)
    if args.debug:
        logging.getLogger("cwltool").setLevel(logging.DEBUG)

    cwl_avsc = os.path.join(module_dir, 'schemas/draft-2/cwl-avro.yml')

    with open(cwl_avsc) as f:
        j = yaml.load(f)
    (ctx, g) = avro_ld.jsonld_context.avrold_to_jsonld_context(j)

    url_fields = []
    for c in ctx:
        if c != "id" and (ctx[c] == "@id") or (isinstance(ctx[c], dict) and ctx[c].get("@type") == "@id"):
            url_fields.append(c)

    if args.print_jsonld_context:
        print json.dumps(ctx, indent=4, sort_keys=True)
        return 0

    if args.print_rdfs:
        print(g.serialize(format=args.rdf_serializer))
        return 0

    if args.print_spec:
        avro_ld.makedoc.avrold_doc(j, sys.stdout)
        return 0

    if args.print_avro:
        names = avro_ld.schema.schema(j)
        print "["
        print ", ".join([json.dumps(names.names[n].to_json(), indent=4, sort_keys=True) for n in names.names])
        print "]"
        return 0

    if not args.workflow:
        _logger.error("CWL document required")
        parser.print_help()
        return 1

    idx = {}
    processobj = from_url(args.workflow, url_fields=url_fields, idx=idx)

    _logger.warn(url_fields)
    #_logger.warn(json.dumps(idx, indent=4))

    if args.print_pre:
        print json.dumps(processobj, indent=4)
        return 0

    validate_links(processobj, url_fields, idx)

    if args.job_order:
        basedir = args.basedir if args.basedir else os.path.abspath(os.path.dirname(args.job_order))
    else:
        basedir = args.basedir

    try:
        t = workflow.makeTool(processobj, basedir, strict=args.strict)
    except (jsonschema.exceptions.ValidationError, avro_ld.validate.ValidationException) as e:
        _logger.error("Tool definition failed validation:\n%s" % e)
        if args.debug:
            _logger.exception()
        return 1
    except RuntimeError as e:
        _logger.error(e)
        if args.debug:
            _logger.exception()
        return 1

    if args.print_rdf:
        printrdf(args.workflow, processobj, ctx, args.rdf_serializer)
        return 0

    if not args.job_order:
        _logger.error("Input object required")
        parser.print_help()
        return 1

    try:
        final_output = []
        def output_callback(out):
            final_output.append(out)

        jobiter = t.job(from_url(args.job_order), basedir, output_callback, use_container=(not args.no_container))
        if args.conformance_test:
            job = jobiter.next()
            a = {"args": job.command_line}
            if job.stdin:
                a["stdin"] = job.stdin
            if job.stdout:
                a["stdout"] = job.stdout
            if job.generatefiles:
                a["generatefiles"] = job.generatefiles
            print json.dumps(a)
        else:
            last = None
            for r in jobiter:
                if r:
                    if args.dry_run:
                        outdir = "/tmp"
                    elif args.outdir:
                        outdir = args.outdir
                    else:
                        outdir = tempfile.mkdtemp()
                    r.run(outdir, dry_run=args.dry_run, pull_image=(not args.no_pull), rm_container=(not args.leave_container))
                else:
                    print "Workflow deadlocked."
                    return 1
                last = r

            _logger.info("Output directory is %s", outdir)
            print json.dumps(final_output[0])
    except (jsonschema.exceptions.ValidationError, validate.ValidationException) as e:
        _logger.error("Input object failed validation:\n%s" % e)
        if args.debug:
            _logger.exception()
        return 1
    except workflow.WorkflowException as e:
        _logger.error("Workflow error:\n%s" % e)
        if args.debug:
            _logger.exception()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
