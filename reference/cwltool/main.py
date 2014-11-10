import tool
import argparse
from ref_resolver import from_url
import jsonschema

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", type=str)
    parser.add_argument("job_order", type=str)
    parser.add_argument("-x", action="store_true", help="Execute")

    args = parser.parse_args()

    try:
        t = tool.Tool(from_url(args.tool))
    except jsonschema.exceptions.ValidationError as e:
        print "Tool definition failed validation"
        print e
        return

    try:
        job = t.job(from_url(args.job_order))
        print '%s%s%s' % (' '.join(job.command_line),
                            ' < %s' % (job.stdin) if job.stdin else '',
                            ' > %s' % (job.stdout) if job.stdout else '')
    except jsonschema.exceptions.ValidationError as e:
        print "Job order failed validation"
        print e
        return
