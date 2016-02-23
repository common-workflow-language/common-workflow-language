import sys
if sys.version_info >= (2,7):
    import typing

def add_dictlist(di, key, val):
    if key not in di:
        di[key] = []
    di[key].append(val)
