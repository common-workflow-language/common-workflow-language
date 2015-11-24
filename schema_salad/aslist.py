def aslist(l):
    """Convenience function to wrap single items and lists, and return lists unchanged."""

    if isinstance(l, list):
        return l
    else:
        return [l]
