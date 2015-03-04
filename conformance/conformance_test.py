#!/usr/bin/env python

import argparse
import json
import os
import subprocess
import sys
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str)
parser.add_argument("--basedir", type=str)
parser.add_argument("tool", type=str)
args = parser.parse_args()

module_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(module_dir, args.test)) as f:
    tests = json.load(f)

failures = 0
for i, t in enumerate(tests):

    shutil.rmtree("conformance_test_tmp", ignore_errors=True)
    os.mkdir("conformance_test_tmp")

    sys.stdout.write("\rTest [%i/%i] " % (i+1, len(tests)))
    sys.stdout.flush()
    out = {}
    try:
        if "output" in t:
            outstr = subprocess.check_output([args.tool,
                                              "--outdir=conformance_test_tmp",
                                              t["tool"],
                                              t["job"]])
        else:
            outstr = subprocess.check_output([args.tool,
                                              "--conformance-test",
                                              "--basedir=" + args.basedir,
                                              "--no-container",
                                              t["tool"],
                                              t["job"]])
        out = json.loads(outstr)
    except ValueError as v:
        print v
        print outstr
    except subprocess.CalledProcessError:
        pass

    pwd = os.path.abspath(os.path.dirname(t["job"]))
    # t["args"] = map(lambda x: x.replace("$PWD", pwd), t["args"])
    # if "stdin" in t:
    #     t["stdin"] = t["stdin"].replace("$PWD", pwd)

    failed = False
    if "output" in t:
        # check the output
        pass
    else:
        for key in ["args", "stdin", "stdout", "generatefiles"]:
            if t.get(key) != out.get(key):
                if not failed:
                    print """Test failed: %s""" % str([args.tool, "--conformance-test", t["tool"], t["job"]])
                    failed = True
                print "%s expected %s\n%s      got %s" % (key, t.get(key), " " * len(key), out.get(key))
        if failed:
            failures += 1

if failures == 0:
    print "All tests passed"
    sys.exit(0)
else:
    print "%i failures" % failures
    sys.exit(1)
