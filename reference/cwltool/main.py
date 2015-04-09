#!/usr/bin/env python

import draft1tool
import draft2tool
import argparse
from ref_resolver import from_url
import jsonschema
import json
import os
import sys
import logging
import workflow
import validate
import tempfile

_logger = logging.getLogger("cwltool")
_logger.addHandler(logging.StreamHandler())


def printrdf(workflow, sr):
    from rdflib import Graph, plugin
    from rdflib.serializer import Serializer
    wf = from_url(workflow)
    g = Graph().parse(data=json.dumps(wf), format='json-ld', location=workflow)
    print(g.serialize(format=sr))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=str)
    parser.add_argument("job_order", type=str, nargs="?", default=None)
    parser.add_argument("--conformance-test", action="store_true")
    parser.add_argument("--basedir", type=str)
    parser.add_argument("--outdir", type=str)
    parser.add_argument("--no-container", action="store_true", help="Do not execute jobs in a Docker container, even when specified by the CommandLineTool")
    parser.add_argument("--leave-container", action="store_true", help="Do not delete Docker container after it exits")
    parser.add_argument("--no-pull", default=False, action="store_true", help="Do not try to pull the Docker image")
    parser.add_argument("--dry-run", action="store_true", help="Do not execute")
    parser.add_argument("--verbose", action="store_true", help="Print more logging")
    parser.add_argument("--debug", action="store_true", help="Print even more logging")
    parser.add_argument("--print-rdf", action="store_true", help="Print corresponding RDF graph for workflow")
    parser.add_argument("--rdf-serializer", help="Output RDF serialization format (one of turtle (default), n3, nt, xml)", default="turtle")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger("cwltool").setLevel(logging.INFO)
    if args.debug:
        logging.getLogger("cwltool").setLevel(logging.DEBUG)

    if args.print_rdf:
        printrdf(args.workflow, args.rdf_serializer)
        return 0

    if not args.job_order:
        _logger.error("Input object required")
        return 1

    basedir = args.basedir if args.basedir else os.path.abspath(os.path.dirname(args.job_order))

    try:
        t = workflow.makeTool(from_url(args.workflow), basedir)
    except (jsonschema.exceptions.ValidationError, validate.ValidationException) as e:
        _logger.error("Tool definition failed validation:\n%s" % e)
        if args.debug:
            _logger.exception()
        return 1
    except RuntimeError as e:
        _logger.error(e)
        if args.debug:
            _logger.exception()
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
