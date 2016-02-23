import sys
if sys.version_info >= (2,7):
    import typing

def aslist(l):
    """Convenience function to wrap single items and lists, and return lists unchanged."""

    if isinstance(l, list):
        return l
    else:
        return [l]
