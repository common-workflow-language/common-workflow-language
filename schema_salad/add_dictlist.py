import sys
from typing import Any, Dict


def add_dictlist(di, key, val):  # type: (Dict, Any, Any) -> None
    if key not in di:
        di[key] = []
    di[key].append(val)
