#!/usr/bin/env python

import argparse
import json
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("tool", type=str)
args = parser.parse_args()

module_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(module_dir, 'conformance_test.json')) as f:
    tests = json.load(f)

for t in tests:
    out = json.loads(subprocess.check_output([args.tool, "--conformance-test", t["tool"], t["job"]]))
    if t["command"] == out:
        print "Passed"
    else:
        print "Failed %s %s" % (t["tool"], t["job"])
        print "expected %s but got %s" % (json.dumps(t["command"]), json.dumps(out))
