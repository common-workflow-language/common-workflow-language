# Copyright (C) The Arvados Authors. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0

import difflib
import json
import re


class JsonDiffMatcher(object):
    """Raise AssertionError with a readable JSON diff when not __eq__().

    Used with assert_called_with() so it's possible for a human to see
    the differences between expected and actual call arguments that
    include non-trivial data structures.
    """
    def __init__(self, expected):
        self.expected = expected

    def __eq__(self, actual):
        expected_json = json.dumps(self.expected, sort_keys=True, indent=2)
        actual_json = json.dumps(actual, sort_keys=True, indent=2)
        if expected_json != actual_json:
            raise AssertionError("".join(difflib.context_diff(
                expected_json.splitlines(1),
                actual_json.splitlines(1),
                fromfile="Expected", tofile="Actual")))
        return True


def StripYAMLComments(yml):
    return re.sub(r'(?ms)^(#.*?\n)*\n*', '', yml)
