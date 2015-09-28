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
import logging

_logger = logging.getLogger("cwltool")
_logger.addHandler(logging.StreamHandler())
_logger.setLevel(logging.INFO)

UNSUPPORTED_FEATURE = 33

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

def run_test(args, i, t):
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
                                 "--quiet",
                                 t["tool"],
                                 t["job"]])
            outstr = subprocess.check_output(test_command)
            out = {"output": json.loads(outstr)}
        else:
            test_command = [args.tool,
                            "--conformance-test",
                            "--basedir=" + args.basedir,
                            "--no-container",
                            "--quiet",
                            t["tool"],
                            t["job"]]

            outstr = subprocess.check_output(test_command)
            out = yaml.load(outstr)
    except ValueError as v:
        _logger.error(v)
        _logger.error(outstr)
    except subprocess.CalledProcessError as err:
        if err.returncode == UNSUPPORTED_FEATURE:
            return UNSUPPORTED_FEATURE
        else:
            _logger.error("""Test failed: %s""", " ".join([pipes.quote(tc) for tc in test_command]))
            _logger.error(t.get("doc"))
            _logger.error("Returned non-zero")
            return 1
    except yaml.scanner.ScannerError as e:
        _logger.error("""Test failed: %s""", " ".join([pipes.quote(tc) for tc in test_command]))
        _logger.error(outstr)
        _logger.error("Parse error %s", str(e))

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
                _logger.warn("""Test failed: %s""", " ".join([pipes.quote(tc) for tc in test_command]))
                _logger.warn(t.get("doc"))
                failed = True
            _logger.warn("%s expected %s\n%s      got %s", key,
                                                            t.get(key),
                                                            " " * len(key),
                                                            out.get(key))

    if outdir:
        shutil.rmtree(outdir)

    if failed:
        return 1
    else:
        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="YAML file describing test cases", required=True)
    parser.add_argument("--basedir", type=str, help="Basedir to use for tests", default=".")
    parser.add_argument("-n", type=int, default=None, help="Run a specific test")
    parser.add_argument("--tool", type=str, default="cwl-runner",
                        help="CWL runner executable to use (default 'cwl-runner'")
    args = parser.parse_args()

    if not args.test:
        parser.print_help()
        return 1

    with open(args.test) as f:
        tests = yaml.load(f)

    failures = 0
    unsupported = 0

    if args.n is not None:
        sys.stderr.write("\rTest [%i/%i] " % (args.n, len(tests)))
        rt = run_test(args, args.n-1, tests[args.n-1])
        if rt == 1:
            failures += 1
        elif rt == UNSUPPORTED_FEATURE:
            unsupported += 1
    else:
        for i, t in enumerate(tests):
            sys.stderr.write("\rTest [%i/%i] " % (i+1, len(tests)))
            sys.stderr.flush()
            rt = run_test(args, i, t)
            if rt == 1:
                failures += 1
            elif rt == UNSUPPORTED_FEATURE:
                unsupported += 1

    if failures == 0 and unsupported == 0:
         _logger.info("All tests passed")
         return 0
    else:
        _logger.warn("%i failures, %i unsupported features", failures, unsupported)
        return 1


if __name__ == "__main__":
    sys.exit(main())
