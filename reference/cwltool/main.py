#!/usr/bin/env python

import draft2tool
import argparse
from avro_ld.ref_resolver import loader
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
import urlparse
import process
import job
from cwlrdf import printrdf, printdot

_logger = logging.getLogger("cwltool")
_logger.addHandler(logging.StreamHandler())

def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=str, nargs="?", default=None)
    parser.add_argument("job_order", type=str, nargs="?", default=None)
    parser.add_argument("--conformance-test", action="store_true")
    parser.add_argument("--basedir", type=str)
    parser.add_argument("--outdir", type=str, default=os.path.abspath('.'),
                        help="Output directory, default current directory")

    parser.add_argument("--no-container", action="store_false", default=True,
                        help="Do not execute jobs in a Docker container, even when specified by the CommandLineTool",
                        dest="use_container")

    parser.add_argument("--rm-container", action="store_true", default=True,
                        help="Delete Docker container used by jobs after they exit (default)",
                        dest="rm_container")

    parser.add_argument("--leave-container", action="store_false",
                        default=True, help="Do not delete Docker container used by jobs after they exit",
                        dest="rm_container")

    parser.add_argument("--rm-tmpdir", action="store_true", default=True,
                        help="Delete intermediate temporary directories (default)",
                        dest="rm_tmpdir")

    parser.add_argument("--leave-tmpdir", action="store_false",
                        default=True, help="Do not delete intermediate temporary directories",
                        dest="rm_tmpdir")

    parser.add_argument("--move-outputs", action="store_true", default=True,
                        help="Move output files to the workflow output directory and delete intermediate output directories (default).",
                        dest="move_outputs")

    parser.add_argument("--leave-outputs", action="store_false", default=True,
                        help="Leave output files in intermediate output directories.",
                        dest="move_outputs")

    parser.add_argument("--enable-pull", default=True, action="store_true",
                        help="Try to pull Docker images", dest="enable_pull")

    parser.add_argument("--disable-pull", default=True, action="store_false",
                        help="Do not try to pull Docker images", dest="enable_pull")

    parser.add_argument("--dry-run", action="store_true",
                        help="Load and validate but do not execute")

    parser.add_argument("--print-rdf", action="store_true",
                        help="Print corresponding RDF graph for workflow and exit")

    parser.add_argument("--rdf-serializer",
                        help="Output RDF serialization format used by --print-rdf (one of turtle (default), n3, nt, xml)",
                        default="turtle")

    parser.add_argument("--print-spec", action="store_true", help="Print HTML specification document and exit")
    parser.add_argument("--print-jsonld-context", action="store_true", help="Print JSON-LD context for CWL file and exit")
    parser.add_argument("--print-rdfs", action="store_true", help="Print JSON-LD context for CWL file and exit")
    parser.add_argument("--print-avro", action="store_true", help="Print Avro schema and exit")
    parser.add_argument("--print-pre", action="store_true", help="Print workflow document after preprocessing and exit")
    parser.add_argument("--print-dot", action="store_true", help="Print workflow visualization in graphviz format and exit")
    parser.add_argument("--strict", action="store_true", help="Strict validation (error on unrecognized fields)")

    parser.add_argument("--verbose", action="store_true", help="Print more logging")
    parser.add_argument("--debug", action="store_true", help="Print even more logging")

    return parser

def single_job_executor(t, job_order, input_basedir, args, **kwargs):
    final_output = []

    def output_callback(out, processStatus):
        if processStatus == "success":
            _logger.info("Overall job status is %s", processStatus)
        else:
            _logger.warn("Overall job status is %s", processStatus)
        final_output.append(out)

    if kwargs.get("outdir"):
        pass
    elif kwargs.get("dry_run"):
        kwargs["outdir"] = "/tmp"
    else:
        kwargs["outdir"] = tempfile.mkdtemp()

    _logger.info("Output directory is %s", kwargs["outdir"])

    jobiter = t.job(job_order,
                    input_basedir,
                    output_callback,
                    **kwargs)

    if kwargs.get("conformance_test"):
        job = jobiter.next()
        a = {"args": job.command_line}
        if job.stdin:
            a["stdin"] = job.pathmapper.mapper(job.stdin)[1]
        if job.stdout:
            a["stdout"] = job.stdout
        if job.generatefiles:
            a["createfiles"] = job.generatefiles
        return a
    else:
        for r in jobiter:
            if r:
                r.run(**kwargs)
            else:
                raise workflow.WorkflowException("Workflow cannot make any more progress.")

        return final_output[0]


def main(args=None, executor=single_job_executor, makeTool=workflow.defaultMakeTool, parser=None):
    if args is None:
        args = sys.argv[1:]

    if parser is None:
        parser = arg_parser()

    args = parser.parse_args(args)

    if args.verbose:
        logging.getLogger("cwltool").setLevel(logging.INFO)
    if args.debug:
        logging.getLogger("cwltool").setLevel(logging.DEBUG)

    (j, names) = process.get_schema()
    (ctx, g) = avro_ld.jsonld_context.avrold_to_jsonld_context(j)

    url_fields = []
    for c in ctx:
        if c != "id" and (ctx[c] == "@id") or (isinstance(ctx[c], dict) and ctx[c].get("@type") == "@id"):
            url_fields.append(c)

    loader.url_fields = url_fields
    loader.idx["cwl:JsonPointer"] = {}

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
        print "["
        print ", ".join([json.dumps(names.names[n].to_json(), indent=4, sort_keys=True) for n in names.names])
        print "]"
        return 0

    if not args.workflow:
        parser.print_help()
        _logger.error("")
        _logger.error("CWL document required")
        return 1

    idx = {}
    try:
        processobj = loader.resolve_ref(args.workflow)
    except (avro_ld.validate.ValidationException, RuntimeError) as e:
        _logger.error("Tool definition failed validation:\n%s" % e)
        if args.debug:
            _logger.exception("")
        return 1

    if args.print_pre:
        print json.dumps(processobj, indent=4)
        return 0

    try:
        loader.validate_links(processobj)
    except (avro_ld.validate.ValidationException) as e:
        _logger.error("Tool definition failed validation:\n%s" % e)
        if args.debug:
            _logger.exception()
        return 1

    if args.job_order:
        input_basedir = args.basedir if args.basedir else os.path.abspath(os.path.dirname(args.job_order))
    else:
        input_basedir = args.basedir

    if isinstance(processobj, list):
        processobj = loader.resolve_ref(urlparse.urljoin(args.workflow, "#main"))

    try:
        t = makeTool(processobj, strict=args.strict, makeTool=makeTool)
    except (avro_ld.validate.ValidationException) as e:
        _logger.error("Tool definition failed validation:\n%s" % e)
        if args.debug:
            _logger.exception("")
        return 1
    except (RuntimeError, workflow.WorkflowException) as e:
        _logger.error(e)
        if args.debug:
            _logger.exception()
        return 1

    if args.print_rdf:
        printrdf(args.workflow, processobj, ctx, args.rdf_serializer)
        return 0

    if args.print_dot:
        printdot(args.workflow, processobj, ctx, args.rdf_serializer)
        return 0

    if not args.job_order:
        parser.print_help()
        _logger.error("")
        _logger.error("Input object required")
        return 1

    try:
        out = executor(t, loader.resolve_ref(args.job_order),
                       input_basedir, args,
                       conformance_test=args.conformance_test,
                       dry_run=args.dry_run,
                       outdir=args.outdir,
                       use_container=args.use_container,
                       pull_image=args.enable_pull,
                       rm_container=args.rm_container,
                       rm_tmpdir=args.rm_tmpdir,
                       makeTool=makeTool,
                       move_outputs=args.move_outputs)
        print json.dumps(out, indent=4)
    except (validate.ValidationException) as e:
        _logger.error("Input object failed validation:\n%s" % e)
        if args.debug:
            _logger.exception("")
        return 1
    except workflow.WorkflowException as e:
        _logger.error("Workflow error:\n  %s" % e)
        if args.debug:
            _logger.exception("")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
