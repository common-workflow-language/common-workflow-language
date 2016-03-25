var cwl = { path: {} };

cwl.path.split = function(p) {
    i = p.lastIndexOf('/') + 1;
    var head = p.slice(0, i);
    var tail = p.slice(i);
    var rep = "";
    for (var i = 0; i < head.length; i++) {
        rep += "/";
    }
    if (head && head != rep) {
        while (head[head.length-1] == "/") {
            head = p.slice(0, head.length-1);
        }
    }
    return [head, tail]
};

cwl.path.dirname = function(path) {
    return cwl.path.split(path)[0];
};

cwl.path.basename = function(path) {
    return cwl.path.split(path)[1];
};

cwl.path.isabs = function(s) {
    return (s[0] == '/');
}

/* TODO: finish porting from Python

cwl.path.splitext = function(p) {
    var sep = "/";
    var extsep = ".";
    var sepIndex = p.rfind(sep);
    var dotIndex = p.rfind(extsep);
    if (dotIndex > sepIndex) {
        // skip all leading dots
        filenameIndex = sepIndex + 1;
        while (filenameIndex < dotIndex) {
            if (p[filenameIndex] != extsep) {
                return p[:dotIndex], p[dotIndex:]
            }
            filenameIndex += 1;
        }
    }
    return p, ''
};


cwl.path.join = function(a) {
    for (b in p) {
        if (b.startswith('/')) {
            path = b;
        }
        else if (path == '' or path.endswith('/')) {
            path +=  b;
        } else {
            path += '/' + b;
        }
    }
    return path;
}

cwl.path.relpath = function(path, start) {
    if not path:
        raise ValueError("no path specified")

    start_list = [x for x in abspath(start).split(sep) if x]
    path_list = [x for x in abspath(path).split(sep) if x]

    # Work out how much of the filepath is shared by start and path.
    i = len(commonprefix([start_list, path_list]))

    rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)
}

cwl.path.normpath = function(path) {
    slash, dot = (u'/', u'.') if isinstance(path, _unicode) else ('/', '.')
    if path == '':
        return dot
    initial_slashes = path.startswith('/')
    # POSIX allows one or two initial slashes, but treats three or more
    # as single slash.
    if (initial_slashes and
        path.startswith('//') and not path.startswith('///')):
        initial_slashes = 2
    comps = path.split('/')
    new_comps = []
    for comp in comps:
        if comp in ('', '.'):
            continue
        if (comp != '..' or (not initial_slashes and not new_comps) or
             (new_comps and new_comps[-1] == '..')):
            new_comps.append(comp)
        elif new_comps:
            new_comps.pop()
    comps = new_comps
    path = slash.join(comps)
    if initial_slashes:
        path = slash*initial_slashes + path
    return path or dot

}
*/
