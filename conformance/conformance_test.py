#!/usr/bin/env python

import argparse
import json
import os
import subprocess
import sys
import shutil
import tempfile
import yaml
import pipes

parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str)
parser.add_argument("--basedir", type=str)
parser.add_argument("-n", type=int, default=None)
parser.add_argument("tool", type=str)
args = parser.parse_args()

module_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(module_dir, args.test)) as f:
    tests = yaml.load(f)

failures = 0

def compare(a, b):
    try:
        if isinstance(a, dict):
            if a.get("class") == "File":
                if not b["path"].endswith("/" + a["path"]):
                    return False
                # ignore empty collections
                b = {k: v for k, v in b.iteritems()
                     if not isinstance(v, (list, dict)) or len(v) > 0}
            if len(a) != len(b):
                return False
            for c in a:
                if a.get("class") != "File" or c != "path":
                    if c not in b:
                        return False
                    if not compare(a[c], b[c]):
                        return False
            return True
        elif isinstance(a, list):
            if len(a) != len(b):
                return False
            for c in xrange(0, len(a)):
                if not compare(a[c], b[c]):
                    return False
            return True
        else:
            return a == b
    except:
        return False

def run_test(i, t):
    global failures
    sys.stdout.write("\rTest [%i/%i] " % (i+1, len(tests)))
    sys.stdout.flush()
    out = {}
    outdir = None
    try:
        if "output" in t:
            test_command = [args.tool]
            # Add prefixes if running on MacOSX so that boot2docker writes to /Users
            if 'darwin' in sys.platform:
                outdir = tempfile.mkdtemp(prefix=os.path.abspath(os.path.curdir))
                test_command.extend(["--tmp-outdir-prefix={}".format(outdir), "--tmpdir-prefix={}".format(outdir)])
            else:
                outdir = tempfile.mkdtemp()
            test_command.extend(["--outdir={}".format(outdir),
                                 "--strict",
                                 t["tool"],
                                 t["job"]])
            outstr = subprocess.check_output(test_command)
            out = {"output": json.loads(outstr)}
        else:
            test_command = [args.tool,
                            "--conformance-test",
                            "--basedir=" + args.basedir,
                            "--no-container",
                            "--strict",
                            t["tool"],
                            t["job"]]

            outstr = subprocess.check_output([args.tool,
                                              "--conformance-test",
                                              "--basedir=" + args.basedir,
                                              "--no-container",
                                              t["tool"],
                                              t["job"]])
            out = yaml.load(outstr)
    except ValueError as v:
        print v
        print outstr
    except subprocess.CalledProcessError:
        print """Test failed: %s""" % " ".join([pipes.quote(tc) for tc in test_command])
        print t.get("doc")
        print "Returned non-zero"
        failures += 1
        return
    except yaml.scanner.ScannerError as e:
        print """Test failed: %s""" % " ".join([pipes.quote(tc) for tc in test_command])
        print outstr
        print "Parse error " + str(e)

    pwd = os.path.abspath(os.path.dirname(t["job"]))
    # t["args"] = map(lambda x: x.replace("$PWD", pwd), t["args"])
    # if "stdin" in t:
    #     t["stdin"] = t["stdin"].replace("$PWD", pwd)

    failed = False
    if "output" in t:
        checkkeys = ["output"]
    else:
        checkkeys = ["args", "stdin", "stdout", "createfiles"]

    for key in checkkeys:
        if not compare(t.get(key), out.get(key)):
            if not failed:
                print """Test failed: %s""" % " ".join([pipes.quote(tc) for tc in test_command])
                print t.get("doc")
                failed = True
            print "%s expected %s\n%s      got %s" % (key, t.get(key), " " * len(key), out.get(key))
    if failed:
        failures += 1

    if outdir:
        shutil.rmtree(outdir)

if __name__ == "__main__":
    if args.n is not None:
        run_test(args.n-1, tests[args.n-1])
    else:
        for i, t in enumerate(tests):
            run_test(i, t)

    if failures == 0:
        print "All tests passed"
        sys.exit(0)
    else:
        print "%i failures" % failures
        sys.exit(1)
