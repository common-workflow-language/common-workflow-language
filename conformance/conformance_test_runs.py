#!/usr/bin/env python

import argparse
import json
import os
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("tool", type=str)
args = parser.parse_args()

module_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(module_dir, 'conformance_test_runs.json')) as f:
    tests = json.load(f)

failures, old_path = 0, os.environ.get('PATH', '')
for i, t in enumerate(tests):
    sys.stdout.write("\rTest [%i/%i] " % (i+1, len(tests)))
    sys.stdout.flush()
    out, outstr = None, ''
    tool_dir = os.path.abspath(os.path.dirname(t['tool']))
    os.environ['PATH'] = ':'.join([tool_dir, old_path])
    try:
        outstr = subprocess.check_output([
            args.tool,
            "--conformance-test-runs",
            "--basedir=test",
            "--no-container",
            t["tool"],
            t["job"]
        ])
        out = json.loads(outstr)
    except ValueError as v:
        print v
        print outstr
    except subprocess.CalledProcessError:
        pass

    if t.get("expected") == out:
        pass
    else:
        print "\nTest failed: " + str([args.tool, "--conformance-test", t["tool"], t["job"]])
        print "  expected %s" % json.dumps(t.get("expected"))
        print "   but got %s" % json.dumps(out)
        print "\n"
        failures += 1

if failures == 0:
    print "All tests passed"
    sys.exit(0)
else:
    print "%i failures" % failures
    sys.exit(1)
