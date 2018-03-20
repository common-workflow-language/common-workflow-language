from __future__ import absolute_import
import ruamel.yaml
from ruamel.yaml.comments import CommentedBase, CommentedMap, CommentedSeq
import re
import os
import traceback

from typing import (Any, AnyStr, Callable, cast, Dict, List, Iterable, Tuple,
                    TypeVar, Union, Text)
import six

lineno_re = re.compile(u"^(.*?:[0-9]+:[0-9]+: )(( *)(.*))")

def _add_lc_filename(r, source):  # type: (ruamel.yaml.comments.CommentedBase, AnyStr) -> None
    if isinstance(r, ruamel.yaml.comments.CommentedBase):
        r.lc.filename = source
    if isinstance(r, list):
        for d in r:
            _add_lc_filename(d, source)
    elif isinstance(r, dict):
        for d in six.itervalues(r):
            _add_lc_filename(d, source)

def relname(source):  # type: (Text) -> Text
    if source.startswith("file://"):
        source = source[7:]
        source = os.path.relpath(source)
    return source

def add_lc_filename(r, source):  # type: (ruamel.yaml.comments.CommentedBase, Text) -> None
    _add_lc_filename(r, relname(source))

def reflow(text, maxline, shift=""):  # type: (Text, int, Text) -> Text
    if maxline < 20:
        maxline = 20
    if len(text) > maxline:
        sp = text.rfind(' ', 0, maxline)
        if sp < 1:
            sp = text.find(' ', sp+1)
            if sp == -1:
                sp = len(text)
        if sp < len(text):
            return "%s\n%s%s" % (text[0:sp], shift, reflow(text[sp+1:], maxline, shift))
    return text

def indent(v, nolead=False, shift=u"  ", bullet=u"  "):  # type: (Text, bool, Text, Text) -> Text
    if nolead:
        return v.splitlines()[0] + u"\n".join([shift + l for l in v.splitlines()[1:]])
    else:
        def lineno(i, l):  # type: (int, Text) -> Text
            r = lineno_re.match(l)
            if bool(r):
                return r.group(1) + (bullet if i == 0 else shift) + r.group(2)
            else:
                return (bullet if i == 0 else shift) + l

        return u"\n".join([lineno(i, l) for i, l in enumerate(v.splitlines())])

def bullets(textlist, bul):  # type: (List[Text], Text) -> Text
    if len(textlist) == 1:
        return textlist[0]
    else:
        return "\n".join(indent(t, bullet=bul) for t in textlist)

def strip_dup_lineno(text, maxline=None):  # type: (Text, int) -> Text
    if maxline is None:
        maxline = int(os.environ.get("COLUMNS", "100"))
    pre = None
    msg = []
    for l in text.splitlines():
        g = lineno_re.match(l)
        if not g:
            msg.append(l)
            continue
        shift = len(g.group(1)) + len(g.group(3))
        g2 = reflow(g.group(2), maxline-shift, " " * shift)
        if g.group(1) != pre:
            pre = g.group(1)
            msg.append(pre + g2)
        else:
            g2 = reflow(g.group(2), maxline-len(g.group(1)), " " * (len(g.group(1))+len(g.group(3))))
            msg.append(" " * len(g.group(1)) + g2)
    return "\n".join(msg)

def cmap(d, lc=None, fn=None):  # type: (Union[int, float, str, Text, Dict, List], List[int], Text) -> Union[int, float, str, Text, CommentedMap, CommentedSeq]
    if lc is None:
        lc = [0, 0, 0, 0]
    if fn is None:
        fn = "test"

    if isinstance(d, CommentedMap):
        fn = d.lc.filename if hasattr(d.lc, "filename") else fn
        for k,v in six.iteritems(d):
            if k in d.lc.data:
                d[k] = cmap(v, lc=d.lc.data[k], fn=fn)
            else:
                d[k] = cmap(v, lc, fn=fn)
        return d
    if isinstance(d, CommentedSeq):
        fn = d.lc.filename if hasattr(d.lc, "filename") else fn
        for k,v in enumerate(d):
            if k in d.lc.data:
                d[k] = cmap(v, lc=d.lc.data[k], fn=fn)
            else:
                d[k] = cmap(v, lc, fn=fn)
        return d
    if isinstance(d, dict):
        cm = CommentedMap()
        for k in sorted(d.keys()):
            v = d[k]
            if isinstance(v, CommentedBase):
                uselc = [v.lc.line, v.lc.col, v.lc.line, v.lc.col]
                vfn = v.lc.filename if hasattr(v.lc, "filename") else fn
            else:
                uselc = lc
                vfn = fn
            cm[k] = cmap(v, lc=uselc, fn=vfn)
            cm.lc.add_kv_line_col(k, uselc)
            cm.lc.filename = fn
        return cm
    if isinstance(d, list):
        cs = CommentedSeq()
        for k,v in enumerate(d):
            if isinstance(v, CommentedBase):
                uselc = [v.lc.line, v.lc.col, v.lc.line, v.lc.col]
                vfn = v.lc.filename if hasattr(v.lc, "filename") else fn
            else:
                uselc = lc
                vfn = fn
            cs.append(cmap(v, lc=uselc, fn=vfn))
            cs.lc.add_kv_line_col(k, uselc)
            cs.lc.filename = fn
        return cs
    else:
        return d

class SourceLine(object):
    def __init__(self, item, key=None, raise_type=six.text_type, include_traceback=False):  # type: (Any, Any, Callable, bool) -> None
        self.item = item
        self.key = key
        self.raise_type = raise_type
        self.include_traceback = include_traceback

    def __enter__(self):  # type: () -> SourceLine
        return self

    def __exit__(self,
                 exc_type,   # type: Any
                 exc_value,  # type: Any
                 tb   # type: Any
                 ):   # -> Any
        if not exc_value:
            return
        if self.include_traceback:
            raise self.makeError("\n".join(traceback.format_exception(exc_type, exc_value, tb)))
        else:
            raise self.makeError(six.text_type(exc_value))

    def makeLead(self):  # type: () -> Text
        if self.key is None or self.item.lc.data is None or self.key not in self.item.lc.data:
            return "%s:%i:%i:" % (self.item.lc.filename if hasattr(self.item.lc, "filename") else "",
                                  (self.item.lc.line or 0)+1,
                                  (self.item.lc.col or 0)+1)
        else:
            return "%s:%i:%i:" % (self.item.lc.filename if hasattr(self.item.lc, "filename") else "",
                                  (self.item.lc.data[self.key][0] or 0)+1,
                                  (self.item.lc.data[self.key][1] or 0)+1)

    def makeError(self, msg):  # type: (Text) -> Any
        if not isinstance(self.item, ruamel.yaml.comments.CommentedBase):
            return self.raise_type(msg)
        errs = []
        lead = self.makeLead()
        for m in msg.splitlines():
            if bool(lineno_re.match(m)):
                errs.append(m)
            else:
                errs.append("%s %s" % (lead, m))
        return self.raise_type("\n".join(errs))
