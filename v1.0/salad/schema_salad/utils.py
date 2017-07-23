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

# http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html

def flatten(l, ltypes=(list, tuple)):
    # type: (Any, Any) -> Any
    if l is None:
        return []
    if not isinstance(l, ltypes):
        return [l]

    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)  # type: ignore
