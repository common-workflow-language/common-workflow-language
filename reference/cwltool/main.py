#!/usr/bin/env python

import tool
import argparse
from ref_resolver import from_url
import jsonschema
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", type=str)
    parser.add_argument("job_order", type=str)
    parser.add_argument("--conformance-test", action="store_true")
    parser.add_argument("--basedir", type=str)
    parser.add_argument("--no-container", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Do not execute")

    args = parser.parse_args()

    try:
        t = tool.Tool(from_url(args.tool))
    except jsonschema.exceptions.ValidationError as e:
        print "Tool definition failed validation"
        print e
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
            print json.dumps(a)
        else:
            print '%s%s%s' % (' '.join(job.command_line),
                                ' < %s' % (job.stdin) if job.stdin else '',
                                ' > %s' % (job.stdout) if job.stdout else '')
            job.run(dry_run=args.dry_run)
    except jsonschema.exceptions.ValidationError as e:
        print "Job order failed validation"
        print e
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
