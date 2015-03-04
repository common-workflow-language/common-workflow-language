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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", type=str)
    parser.add_argument("job_order", type=str)
    parser.add_argument("--conformance-test", action="store_true")
    parser.add_argument("--basedir", type=str)
    parser.add_argument("--outdir", type=str)
    parser.add_argument("--no-container", action="store_true", help="Do not execute in a Docker container, even if one is specified in the tool file")
    parser.add_argument("--no-pull", default=False, action="store_true", help="Do not try to pull the Docker image")
    parser.add_argument("--dry-run", action="store_true", help="Do not execute")

    args = parser.parse_args()

    try:
        u = from_url(args.tool)
        if "schema" in u:
            t = draft1tool.Tool(u)
        else:
            t = draft2tool.Tool(u)
    except (jsonschema.exceptions.ValidationError, draft2tool.ValidationException):
        logging.exception("Tool definition failed validation")
        return 1

    basedir = args.basedir if args.basedir else os.path.abspath(os.path.dirname(args.job_order))

    try:
        job = t.job(from_url(args.job_order), basedir, use_container=(not args.no_container))
        if args.conformance_test:
            a = {"args": job.command_line}
            if job.stdin:
                a["stdin"] = job.stdin
            if job.stdout:
                a["stdout"] = job.stdout
            if job.generatefiles:
                a["generatefiles"] = job.generatefiles
            print json.dumps(a)
        else:
            logging.info('%s%s%s', ' '.join(job.command_line),
                                ' < %s' % (job.stdin) if job.stdin else '',
                                ' > %s' % (job.stdout) if job.stdout else '')

            runjob = job.run(dry_run=args.dry_run, pull_image=(not args.no_pull), outdir=args.outdir)
            print json.dumps(runjob)
    except jsonschema.exceptions.ValidationError:
        logging.exception("Job order failed validation")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
