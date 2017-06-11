from __future__ import absolute_import

from typing import Any, Dict, List


def add_dictlist(di, key, val):  # type: (Dict, Any, Any) -> None
    if key not in di:
        di[key] = []
    di[key].append(val)


def aslist(l):  # type: (Any) -> List
    """Convenience function to wrap single items and lists, and return lists unchanged."""

    if isinstance(l, list):
        return l
    else:
        return [l]
