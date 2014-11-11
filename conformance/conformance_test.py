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
with open(os.path.join(module_dir, 'conformance_test.json')) as f:
    tests = json.load(f)

failures = 0
for i, t in enumerate(tests):
    print "\rTest [%i/%i]" % (i+1, len(tests))
    out = json.loads(subprocess.check_output([args.tool, "--conformance-test", t["tool"], t["job"]]))
    if t["args"] == out["args"] and t.get("stdin") == out.get("stdin") and t.get("stdout") == out.get("stdout"):
        pass
    else:
        print "\nTest failed: tool %s   job %s" % (t["tool"], t["job"])
        print "  expected %s (stdin %s) (stdout %s)" % (json.dumps(t["args"]), json.dumps(t.get("stdin")), json.dumps(t.get("stdout")))
        print "   but got %s (stdin %s) (stdout %s)" % (json.dumps(out["args"]), json.dumps(out.get("stdin")), json.dumps(out.get("stdout")))
        failures += 1

if failures == 0:
    print "All tests passed"
    sys.exit(0)
else:
    print "%i failures" % failures
    sys.exit(1)
