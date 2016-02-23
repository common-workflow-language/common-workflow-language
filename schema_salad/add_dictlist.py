def add_dictlist(di, key, val):
    if key not in di:
        di[key] = []
    di[key].append(val)
