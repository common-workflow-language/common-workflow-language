from __future__ import absolute_import
import unittest
import sys

import schema_salad.main as cli_parser

# for capturing print() output
from contextlib import contextmanager
from six import StringIO

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


""" test different sets of command line arguments"""
class ParseCliArgs(unittest.TestCase):

    def test_version(self):
        args = [["--version"], ["-v"]]
        for arg in args:
            with captured_output() as (out, err):
                cli_parser.main(arg)

            response = out.getvalue().strip()  # capture output and strip newline
            self.assertTrue("Current version" in response)

    def test_empty_input(self):
        # running schema_salad tool wihtout any args
        args = []
        with captured_output() as (out, err):
            cli_parser.main(args)

        response = out.getvalue().strip()
        self.assertTrue("error: too few arguments" in response)
