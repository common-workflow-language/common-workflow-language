from __future__ import absolute_import
import sys
import os
import json
import hashlib
import logging
import collections
from io import open

import six
from six.moves import range
from six.moves import urllib
from six import StringIO

import re
import copy


from . import validate
from .utils import aslist, flatten
from .sourceline import SourceLine, add_lc_filename, relname

import requests
from cachecontrol.wrapper import CacheControl
from cachecontrol.caches import FileCache
import ruamel.yaml as yaml
from ruamel.yaml.comments import CommentedSeq, CommentedMap

import rdflib
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, OWL
from rdflib.plugins.parsers.notation3 import BadSyntax
import xml.sax
from typing import (cast, Any, AnyStr, Callable, Dict, List, Iterable,
        Optional, Set, Text, Tuple, TypeVar, Union)


_logger = logging.getLogger("salad")
ContextType = Dict[six.text_type, Union[Dict, six.text_type, Iterable[six.text_type]]]
DocumentType = TypeVar('DocumentType', CommentedSeq, CommentedMap)
DocumentOrStrType = TypeVar(
    'DocumentOrStrType', CommentedSeq, CommentedMap, six.text_type)

def file_uri(path, split_frag=False):  # type: (str, bool) -> str
    if path.startswith("file://"):
        return path
    if split_frag:
        pathsp = path.split("#", 2)
        frag = "#" + urllib.parse.quote(str(pathsp[1])) if len(pathsp) == 2 else ""
        urlpath = urllib.request.pathname2url(str(pathsp[0]))
    else:
        urlpath = urllib.request.pathname2url(path)
        frag = ""
    if urlpath.startswith("//"):
        return "file:%s%s" % (urlpath, frag)
    else:
        return "file://%s%s" % (urlpath, frag)

def uri_file_path(url):  # type: (str) -> str
    split = urllib.parse.urlsplit(url)
    if split.scheme == "file":
        return urllib.request.url2pathname(
            str(split.path)) + ("#" + urllib.parse.unquote(str(split.fragment))
                if bool(split.fragment) else "")
    else:
        raise ValueError("Not a file URI")

class NormDict(CommentedMap):

    def __init__(self, normalize=six.text_type):  # type: (Callable) -> None
        super(NormDict, self).__init__()
        self.normalize = normalize

    def __getitem__(self, key):  # type: (Any) -> Any
        return super(NormDict, self).__getitem__(self.normalize(key))

    def __setitem__(self, key, value):  # type: (Any, Any) -> Any
        return super(NormDict, self).__setitem__(self.normalize(key), value)

    def __delitem__(self, key):  # type: (Any) -> Any
        return super(NormDict, self).__delitem__(self.normalize(key))

    def __contains__(self, key):  # type: (Any) -> Any
        return super(NormDict, self).__contains__(self.normalize(key))


def merge_properties(a, b):  # type: (List[Any], List[Any]) -> Dict[Any, Any]
    c = {}
    for i in a:
        if i not in b:
            c[i] = a[i]
    for i in b:
        if i not in a:
            c[i] = b[i]
    for i in a:
        if i in b:
            c[i] = aslist(a[i]) + aslist(b[i])

    return c


def SubLoader(loader):  # type: (Loader) -> Loader
    return Loader(loader.ctx, schemagraph=loader.graph,
                  foreign_properties=loader.foreign_properties, idx=loader.idx,
                  cache=loader.cache, fetcher_constructor=loader.fetcher_constructor,
                  skip_schemas=loader.skip_schemas)

class Fetcher(object):
    def fetch_text(self, url):    # type: (Text) -> Text
        raise NotImplementedError()

    def check_exists(self, url):  # type: (Text) -> bool
        raise NotImplementedError()

    def urljoin(self, base_url, url):  # type: (Text, Text) -> Text
        raise NotImplementedError()


class DefaultFetcher(Fetcher):
    def __init__(self,
                 cache,   # type: Dict[Text, Text]
                 session  # type: Optional[requests.sessions.Session]
                 ):  # type: (...) -> None
        self.cache = cache
        self.session = session

    def fetch_text(self, url):
        # type: (Text) -> Text
        if url in self.cache:
            return self.cache[url]

        split = urllib.parse.urlsplit(url)
        scheme, path = split.scheme, split.path

        if scheme in [u'http', u'https'] and self.session is not None:
            try:
                resp = self.session.get(url)
                resp.raise_for_status()
            except Exception as e:
                raise RuntimeError(url, e)
            return resp.text
        elif scheme == 'file':
            try:
                # On Windows, url.path will be /drive:/path ; on Unix systems,
                # /path. As we want drive:/path instead of /drive:/path on Windows,
                # remove the leading /.
                if os.path.isabs(path[1:]):  # checking if pathis valid after removing front / or not
                    path = path[1:]
                with open(urllib.request.url2pathname(str(path)), encoding='utf-8') as fp:
                    return fp.read()

            except (OSError, IOError) as e:
                if e.filename == path:
                    raise RuntimeError(six.text_type(e))
                else:
                    raise RuntimeError('Error reading %s: %s' % (url, e))
        else:
            raise ValueError('Unsupported scheme in url: %s' % url)

    def check_exists(self, url):  # type: (Text) -> bool
        if url in self.cache:
            return True

        split = urllib.parse.urlsplit(url)
        scheme, path = split.scheme, split.path

        if scheme in [u'http', u'https'] and self.session is not None:
            try:
                resp = self.session.head(url)
                resp.raise_for_status()
            except Exception as e:
                return False
            return True
        elif scheme == 'file':
            return os.path.exists(urllib.request.url2pathname(str(path)))
        else:
            raise ValueError('Unsupported scheme in url: %s' % url)

    def urljoin(self, base_url, url):  # type: (Text, Text) -> Text

        # On windows urljoin consider drive name as scheme and forces it over base url's scheme,
        # here we are forcing base url's scheme over url
        if sys.platform == 'win32':
            if (base_url == url):
                return url
            basesplit = urllib.parse.urlsplit(base_url)
            if basesplit.scheme:
                split = urllib.parse.urlsplit(url)
                if split.scheme:
                    if split.scheme in ['http','https','file']:
                        url = urllib.parse.urlunsplit(('', split.netloc, split.path, split.query, split.fragment))
                    else:
                        url= urllib.parse.urlunsplit((basesplit.scheme, split.netloc, urllib.parse.urlunsplit((split.scheme, '', split.path,'', '')), split.query, split.fragment))
            return urllib.parse.urljoin(base_url, url)
        else:
            return urllib.parse.urljoin(base_url, url)

class Loader(object):
    def __init__(self,
                 ctx,                       # type: ContextType
                 schemagraph=None,          # type: rdflib.graph.Graph
                 foreign_properties=None,   # type: Set[Text]
                 idx=None,                  # type: Dict[Text, Union[CommentedMap, CommentedSeq, Text, None]]
                 cache=None,                # type: Dict[Text, Any]
                 session=None,              # type: requests.sessions.Session
                 fetcher_constructor=None,  # type: Callable[[Dict[Text, Text], requests.sessions.Session], Fetcher]
                 skip_schemas=None          # type: bool
                 ):
        # type: (...) -> None

        normalize = lambda url: urllib.parse.urlsplit(url).geturl()
        if idx is not None:
            self.idx = idx
        else:
            self.idx = NormDict(normalize)

        self.ctx = {}       # type: ContextType
        if schemagraph is not None:
            self.graph = schemagraph
        else:
            self.graph = rdflib.graph.Graph()

        if foreign_properties is not None:
            self.foreign_properties = foreign_properties
        else:
            self.foreign_properties = set()

        if cache is not None:
            self.cache = cache
        else:
            self.cache = {}

        if skip_schemas is not None:
            self.skip_schemas = skip_schemas
        else:
            self.skip_schemas = False

        if session is None:
            if "HOME" in os.environ:
                self.session = CacheControl(
                    requests.Session(),
                    cache=FileCache(os.path.join(os.environ["HOME"], ".cache", "salad")))
            elif "TMP" in os.environ:
                self.session = CacheControl(
                    requests.Session(),
                    cache=FileCache(os.path.join(os.environ["TMP"], ".cache", "salad")))
            else:
                self.session = CacheControl(
                    requests.Session(),
                    cache=FileCache("/tmp", ".cache", "salad"))
        else:
            self.session = session

        if fetcher_constructor is not None:
            self.fetcher_constructor = fetcher_constructor
        else:
            self.fetcher_constructor = DefaultFetcher
        self.fetcher = self.fetcher_constructor(self.cache, self.session)

        self.fetch_text = self.fetcher.fetch_text
        self.check_exists = self.fetcher.check_exists

        self.url_fields = set()         # type: Set[Text]
        self.scoped_ref_fields = {}     # type: Dict[Text, int]
        self.vocab_fields = set()       # type: Set[Text]
        self.identifiers = []           # type: List[Text]
        self.identity_links = set()     # type: Set[Text]
        self.standalone = None          # type: Optional[Set[Text]]
        self.nolinkcheck = set()        # type: Set[Text]
        self.vocab = {}                 # type: Dict[Text, Text]
        self.rvocab = {}                # type: Dict[Text, Text]
        self.idmap = {}                 # type: Dict[Text, Any]
        self.mapPredicate = {}          # type: Dict[Text, Text]
        self.type_dsl_fields = set()    # type: Set[Text]

        self.add_context(ctx)

    def expand_url(self,
                   url,                 # type: Text
                   base_url,            # type: Text
                   scoped_id=False,     # type: bool
                   vocab_term=False,    # type: bool
                   scoped_ref=None      # type: int
                   ):
        # type: (...) -> Text
        if url in (u"@id", u"@type"):
            return url

        if vocab_term and url in self.vocab:
            return url

        if bool(self.vocab) and u":" in url:
            prefix = url.split(u":")[0]
            if prefix in self.vocab:
                url = self.vocab[prefix] + url[len(prefix) + 1:]

        split = urllib.parse.urlsplit(url)

        if ((bool(split.scheme) and split.scheme in [u'http', u'https', u'file']) or url.startswith(u"$(")
            or url.startswith(u"${")):
            pass
        elif scoped_id and not bool(split.fragment):
            splitbase = urllib.parse.urlsplit(base_url)
            frg = u""
            if bool(splitbase.fragment):
                frg = splitbase.fragment + u"/" + split.path
            else:
                frg = split.path
            pt = splitbase.path if splitbase.path != '' else "/"
            url = urllib.parse.urlunsplit(
                (splitbase.scheme, splitbase.netloc, pt, splitbase.query, frg))
        elif scoped_ref is not None and not split.fragment:
            pass
        else:
            url = self.fetcher.urljoin(base_url, url)

        if vocab_term and url in self.rvocab:
            return self.rvocab[url]
        else:
            return url

    def _add_properties(self, s):  # type: (Text) -> None
        for _, _, rng in self.graph.triples((s, RDFS.range, None)):
            literal = ((six.text_type(rng).startswith(
                u"http://www.w3.org/2001/XMLSchema#") and
                not six.text_type(rng) == u"http://www.w3.org/2001/XMLSchema#anyURI")
                or six.text_type(rng) ==
                u"http://www.w3.org/2000/01/rdf-schema#Literal")
            if not literal:
                self.url_fields.add(six.text_type(s))
        self.foreign_properties.add(six.text_type(s))

    def add_namespaces(self, ns):  # type: (Dict[Text, Text]) -> None
        self.vocab.update(ns)

    def add_schemas(self, ns, base_url):
        # type: (Union[List[Text], Text], Text) -> None
        if self.skip_schemas:
            return
        for sch in aslist(ns):
            fetchurl = self.fetcher.urljoin(base_url, sch)
            if fetchurl not in self.cache:
                _logger.debug("Getting external schema %s", fetchurl)
                content = self.fetch_text(fetchurl)
                self.cache[fetchurl] = rdflib.graph.Graph()
                for fmt in ['xml', 'turtle', 'rdfa']:
                    try:
                        self.cache[fetchurl].parse(data=content, format=fmt, publicID=str(fetchurl))
                        self.graph += self.cache[fetchurl]
                        break
                    except xml.sax.SAXParseException:
                        pass
                    except TypeError:
                        pass
                    except BadSyntax:
                        pass

        for s, _, _ in self.graph.triples((None, RDF.type, RDF.Property)):
            self._add_properties(s)
        for s, _, o in self.graph.triples((None, RDFS.subPropertyOf, None)):
            self._add_properties(s)
            self._add_properties(o)
        for s, _, _ in self.graph.triples((None, RDFS.range, None)):
            self._add_properties(s)
        for s, _, _ in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            self._add_properties(s)

        for s, _, _ in self.graph.triples((None, None, None)):
            self.idx[six.text_type(s)] = None

    def add_context(self, newcontext, baseuri=""):
        # type: (ContextType, Text) -> None
        if bool(self.vocab):
            raise validate.ValidationException(
                "Refreshing context that already has stuff in it")

        self.url_fields = set(("$schemas",))
        self.scoped_ref_fields = {}
        self.vocab_fields = set()
        self.identifiers = []
        self.identity_links = set()
        self.standalone = set()
        self.nolinkcheck = set()
        self.idmap = {}
        self.mapPredicate = {}
        self.vocab = {}
        self.rvocab = {}
        self.type_dsl_fields = set()

        self.ctx.update(_copy_dict_without_key(newcontext, u"@context"))

        _logger.debug("ctx is %s", self.ctx)

        for key, value in self.ctx.items():
            if value == u"@id":
                self.identifiers.append(key)
                self.identity_links.add(key)
            elif isinstance(value, dict) and value.get(u"@type") == u"@id":
                self.url_fields.add(key)
                if u"refScope" in value:
                    self.scoped_ref_fields[key] = value[u"refScope"]
                if value.get(u"identity", False):
                    self.identity_links.add(key)
            elif isinstance(value, dict) and value.get(u"@type") == u"@vocab":
                self.url_fields.add(key)
                self.vocab_fields.add(key)
                if u"refScope" in value:
                    self.scoped_ref_fields[key] = value[u"refScope"]
                if value.get(u"typeDSL"):
                    self.type_dsl_fields.add(key)
            if isinstance(value, dict) and value.get(u"noLinkCheck"):
                self.nolinkcheck.add(key)

            if isinstance(value, dict) and value.get(u"mapSubject"):
                self.idmap[key] = value[u"mapSubject"]

            if isinstance(value, dict) and value.get(u"mapPredicate"):
                self.mapPredicate[key] = value[u"mapPredicate"]

            if isinstance(value, dict) and u"@id" in value:
                self.vocab[key] = value[u"@id"]
            elif isinstance(value, six.string_types):
                self.vocab[key] = value

        for k, v in self.vocab.items():
            self.rvocab[self.expand_url(v, u"", scoped_id=False)] = k

        self.identifiers.sort()

        _logger.debug("identifiers is %s", self.identifiers)
        _logger.debug("identity_links is %s", self.identity_links)
        _logger.debug("url_fields is %s", self.url_fields)
        _logger.debug("vocab_fields is %s", self.vocab_fields)
        _logger.debug("vocab is %s", self.vocab)

    def resolve_ref(self,
                    ref,             # type: Union[CommentedMap, CommentedSeq, Text]
                    base_url=None,   # type: Text
                    checklinks=True  # type: bool
                    ):
        # type: (...) -> Tuple[Union[CommentedMap, CommentedSeq, Text, None], Dict[Text, Any]]

        lref = ref           # type: Union[CommentedMap, CommentedSeq, Text, None]
        obj = None           # type: Optional[CommentedMap]
        resolved_obj = None  # type: Optional[Union[CommentedMap, CommentedSeq, Text]]
        inc = False
        mixin = None         # type: Optional[Dict[Text, Any]]

        if not base_url:
            base_url = file_uri(os.getcwd()) + "/"

        sl = SourceLine(obj, None, ValueError)
        # If `ref` is a dict, look for special directives.
        if isinstance(lref, CommentedMap):
            obj = lref
            if "$import" in obj:
                sl = SourceLine(obj, "$import", RuntimeError)
                if len(obj) == 1:
                    lref = obj[u"$import"]
                    obj = None
                else:
                    raise sl.makeError(
                        u"'$import' must be the only field in %s"
                        % (six.text_type(obj)))
            elif "$include" in obj:
                sl = SourceLine(obj, "$include", RuntimeError)
                if len(obj) == 1:
                    lref = obj[u"$include"]
                    inc = True
                    obj = None
                else:
                    raise sl.makeError(
                        u"'$include' must be the only field in %s"
                        % (six.text_type(obj)))
            elif "$mixin" in obj:
                sl = SourceLine(obj, "$mixin", RuntimeError)
                lref = obj[u"$mixin"]
                mixin = obj
                obj = None
            else:
                lref = None
                for identifier in self.identifiers:
                    if identifier in obj:
                        lref = obj[identifier]
                        break
                if not lref:
                    raise sl.makeError(
                        u"Object `%s` does not have identifier field in %s"
                        % (relname(obj), self.identifiers))

        if not isinstance(lref, (str, six.text_type)):
            raise ValueError(u"Expected CommentedMap or string, got %s: `%s`"
                    % (type(lref), six.text_type(lref)))

        if isinstance(lref, (str, six.text_type)) and os.sep == "\\":
            # Convert Windows path separator in ref
            lref = lref.replace("\\", "/")

        url = self.expand_url(lref, base_url, scoped_id=(obj is not None))
        # Has this reference been loaded already?
        if url in self.idx and (not mixin):
            return self.idx[url], {}

        sl.raise_type = RuntimeError
        with sl:
            # "$include" directive means load raw text
            if inc:
                return self.fetch_text(url), {}

            doc = None
            if isinstance(obj, collections.MutableMapping):
                for identifier in self.identifiers:
                    obj[identifier] = url
                doc_url = url
            else:
                # Load structured document
                doc_url, frg = urllib.parse.urldefrag(url)
                if doc_url in self.idx and (not mixin):
                    # If the base document is in the index, it was already loaded,
                    # so if we didn't find the reference earlier then it must not
                    # exist.
                    raise validate.ValidationException(
                        u"Reference `#%s` not found in file `%s`."
                        % (frg, doc_url))
                doc = self.fetch(doc_url, inject_ids=(not mixin))

        # Recursively expand urls and resolve directives
        if bool(mixin):
            doc = copy.deepcopy(doc)
            doc.update(mixin)
            del doc["$mixin"]
            resolved_obj, metadata = self.resolve_all(
                doc, base_url, file_base=doc_url, checklinks=checklinks)
        else:
            resolved_obj, metadata = self.resolve_all(
                doc if doc else obj, doc_url, checklinks=checklinks)

        # Requested reference should be in the index now, otherwise it's a bad
        # reference
        if not bool(mixin):
            if url in self.idx:
                resolved_obj = self.idx[url]
            else:
                raise RuntimeError(
                    "Reference `%s` is not in the index. Index contains:\n  %s"
                    % (url, "\n  ".join(self.idx)))

        if isinstance(resolved_obj, CommentedMap):
            if u"$graph" in resolved_obj:
                metadata = _copy_dict_without_key(resolved_obj, u"$graph")
                return resolved_obj[u"$graph"], metadata
            else:
                return resolved_obj, metadata
        else:
            return resolved_obj, metadata

    def _resolve_idmap(self,
                       document,    # type: CommentedMap
                       loader       # type: Loader
                       ):
        # type: (...) -> None
        # Convert fields with mapSubject into lists
        # use mapPredicate if the mapped value isn't a dict.
        for idmapField in loader.idmap:
            if (idmapField in document):
                idmapFieldValue = document[idmapField]
                if (isinstance(idmapFieldValue, dict)
                        and "$import" not in idmapFieldValue
                        and "$include" not in idmapFieldValue):
                    ls = CommentedSeq()
                    for k in sorted(idmapFieldValue.keys()):
                        val = idmapFieldValue[k]
                        v = None  # type: Optional[CommentedMap]
                        if not isinstance(val, CommentedMap):
                            if idmapField in loader.mapPredicate:
                                v = CommentedMap(
                                    ((loader.mapPredicate[idmapField], val),))
                                v.lc.add_kv_line_col(
                                    loader.mapPredicate[idmapField],
                                    document[idmapField].lc.data[k])
                                v.lc.filename = document.lc.filename
                            else:
                                raise validate.ValidationException(
                                    "mapSubject '%s' value '%s' is not a dict"
                                    "and does not have a mapPredicate", k, v)
                        else:
                            v = val

                        v[loader.idmap[idmapField]] = k
                        v.lc.add_kv_line_col(loader.idmap[idmapField],
                                             document[idmapField].lc.data[k])
                        v.lc.filename = document.lc.filename

                        ls.lc.add_kv_line_col(
                            len(ls), document[idmapField].lc.data[k])

                        ls.lc.filename = document.lc.filename
                        ls.append(v)

                    document[idmapField] = ls

    typeDSLregex = re.compile(u"^([^[?]+)(\[\])?(\?)?$")

    def _type_dsl(self,
                  t,        # type: Union[Text, Dict, List]
                  lc,
                  filename):
        # type: (...) -> Union[Text, Dict[Text, Text], List[Union[Text, Dict[Text, Text]]]]

        if not isinstance(t, (str, six.text_type)):
            return t

        m = Loader.typeDSLregex.match(t)
        if not m:
            return t
        first = m.group(1)
        second = third = None
        if bool(m.group(2)):
            second = CommentedMap((("type", "array"),
                                   ("items", first)))
            second.lc.add_kv_line_col("type", lc)
            second.lc.add_kv_line_col("items", lc)
            second.lc.filename = filename
        if bool(m.group(3)):
            third = CommentedSeq([u"null", second or first])
            third.lc.add_kv_line_col(0, lc)
            third.lc.add_kv_line_col(1, lc)
            third.lc.filename = filename
        return third or second or first

    def _resolve_type_dsl(self,
                          document,  # type: CommentedMap
                          loader     # type: Loader
                          ):
        # type: (...) -> None
        for d in loader.type_dsl_fields:
            if d in document:
                datum2 = datum = document[d]
                if isinstance(datum, (str, six.text_type)):
                    datum2 = self._type_dsl(datum, document.lc.data[
                                            d], document.lc.filename)
                elif isinstance(datum, CommentedSeq):
                    datum2 = CommentedSeq()
                    for n, t in enumerate(datum):
                        datum2.lc.add_kv_line_col(
                            len(datum2), datum.lc.data[n])
                        datum2.append(self._type_dsl(
                            t, datum.lc.data[n], document.lc.filename))
                if isinstance(datum2, CommentedSeq):
                    datum3 = CommentedSeq()
                    seen = []  # type: List[Text]
                    for i, item in enumerate(datum2):
                        if isinstance(item, CommentedSeq):
                            for j, v in enumerate(item):
                                if v not in seen:
                                    datum3.lc.add_kv_line_col(
                                        len(datum3), item.lc.data[j])
                                    datum3.append(v)
                                    seen.append(v)
                        else:
                            if item not in seen:
                                datum3.lc.add_kv_line_col(
                                    len(datum3), datum2.lc.data[i])
                                datum3.append(item)
                                seen.append(item)
                    document[d] = datum3
                else:
                    document[d] = datum2

    def _resolve_identifier(self, document, loader, base_url):
        # type: (CommentedMap, Loader, Text) -> Text
        # Expand identifier field (usually 'id') to resolve scope
        for identifer in loader.identifiers:
            if identifer in document:
                if isinstance(document[identifer], six.string_types):
                    document[identifer] = loader.expand_url(
                        document[identifer], base_url, scoped_id=True)
                    if (document[identifer] not in loader.idx
                            or isinstance(
                                loader.idx[document[identifer]], six.string_types)):
                        loader.idx[document[identifer]] = document
                    base_url = document[identifer]
                else:
                    raise validate.ValidationException(
                        "identifier field '%s' must be a string"
                        % (document[identifer]))
        return base_url

    def _resolve_identity(self, document, loader, base_url):
        # type: (Dict[Text, List[Text]], Loader, Text) -> None
        # Resolve scope for identity fields (fields where the value is the
        # identity of a standalone node, such as enum symbols)
        for identifer in loader.identity_links:
            if identifer in document and isinstance(document[identifer], list):
                for n, v in enumerate(document[identifer]):
                    if isinstance(document[identifer][n], six.string_types):
                        document[identifer][n] = loader.expand_url(
                            document[identifer][n], base_url, scoped_id=True)
                        if document[identifer][n] not in loader.idx:
                            loader.idx[document[identifer][
                                n]] = document[identifer][n]

    def _normalize_fields(self, document, loader):
        # type: (Dict[Text, Text], Loader) -> None
        # Normalize fields which are prefixed or full URIn to vocabulary terms
        for d in list(document.keys()):
            d2 = loader.expand_url(d, u"", scoped_id=False, vocab_term=True)
            if d != d2:
                document[d2] = document[d]
                del document[d]

    def _resolve_uris(self,
                      document,  # type: Dict[Text, Union[Text, List[Text]]]
                      loader,    # type: Loader
                      base_url   # type: Text
                      ):
        # type: (...) -> None
        # Resolve remaining URLs based on document base
        for d in loader.url_fields:
            if d in document:
                datum = document[d]
                if isinstance(datum, (str, six.text_type)):
                    document[d] = loader.expand_url(
                        datum, base_url, scoped_id=False,
                        vocab_term=(d in loader.vocab_fields),
                        scoped_ref=self.scoped_ref_fields.get(d))
                elif isinstance(datum, list):
                    for i, url in enumerate(datum):
                        if isinstance(url, (str, six.text_type)):
                            datum[i] = loader.expand_url(
                                url, base_url, scoped_id=False,
                                vocab_term=(d in loader.vocab_fields),
                                scoped_ref=self.scoped_ref_fields.get(d))


    def resolve_all(self,
                    document,           # type: Union[CommentedMap, CommentedSeq]
                    base_url,           # type: Text
                    file_base=None,     # type: Text
                    checklinks=True     # type: bool
                    ):
        # type: (...) -> Tuple[Union[CommentedMap, CommentedSeq, Text, None], Dict[Text, Any]]
        loader = self
        metadata = CommentedMap()  # type: CommentedMap
        if file_base is None:
            file_base = base_url

        if isinstance(document, CommentedMap):
            # Handle $import and $include
            if (u'$import' in document or u'$include' in document):
                return self.resolve_ref(
                    document, base_url=file_base, checklinks=checklinks)
            elif u'$mixin' in document:
                return self.resolve_ref(
                    document, base_url=base_url, checklinks=checklinks)
        elif isinstance(document, CommentedSeq):
            pass
        elif isinstance(document, (list, dict)):
            raise Exception("Expected CommentedMap or CommentedSeq, got %s: `%s`" % (type(document), document))
        else:
            return (document, metadata)

        newctx = None  # type: Optional[Loader]
        if isinstance(document, CommentedMap):
            # Handle $base, $profile, $namespaces, $schemas and $graph
            if u"$base" in document:
                base_url = document[u"$base"]

            if u"$profile" in document:
                if newctx is None:
                    newctx = SubLoader(self)
                prof = self.fetch(document[u"$profile"])
                newctx.add_namespaces(document.get(u"$namespaces", {}))
                newctx.add_schemas(document.get(
                    u"$schemas", []), document[u"$profile"])

            if u"$namespaces" in document:
                if newctx is None:
                    newctx = SubLoader(self)
                newctx.add_namespaces(document[u"$namespaces"])

            if u"$schemas" in document:
                if newctx is None:
                    newctx = SubLoader(self)
                newctx.add_schemas(document[u"$schemas"], file_base)

            if newctx is not None:
                loader = newctx

            if u"$graph" in document:
                metadata = _copy_dict_without_key(document, u"$graph")
                document = document[u"$graph"]
                resolved_metadata = loader.resolve_all(
                    metadata, base_url, file_base=file_base,
                    checklinks=False)[0]
                if isinstance(resolved_metadata, dict):
                    metadata = resolved_metadata
                else:
                    raise validate.ValidationException(
                        "Validation error, metadata must be dict: %s"
                        % (resolved_metadata))

        if isinstance(document, CommentedMap):
            self._normalize_fields(document, loader)
            self._resolve_idmap(document, loader)
            self._resolve_type_dsl(document, loader)
            base_url = self._resolve_identifier(document, loader, base_url)
            self._resolve_identity(document, loader, base_url)
            self._resolve_uris(document, loader, base_url)

            try:
                for key, val in document.items():
                    document[key], _ = loader.resolve_all(
                        val, base_url, file_base=file_base, checklinks=False)
            except validate.ValidationException as v:
                _logger.warn("loader is %s", id(loader), exc_info=True)
                raise validate.ValidationException("(%s) (%s) Validation error in field %s:\n%s" % (
                    id(loader), file_base, key, validate.indent(six.text_type(v))))

        elif isinstance(document, CommentedSeq):
            i = 0
            try:
                while i < len(document):
                    val = document[i]
                    if isinstance(val, CommentedMap) and (u"$import" in val or u"$mixin" in val):
                        l, _ = loader.resolve_ref(
                            val, base_url=file_base, checklinks=False)
                        if isinstance(l, CommentedSeq):
                            lc = document.lc.data[i]
                            del document[i]
                            llen = len(l)
                            for j in range(len(document) + llen, i + llen, -1):
                                document.lc.data[
                                    j - 1] = document.lc.data[j - llen]
                            for item in l:
                                document.insert(i, item)
                                document.lc.data[i] = lc
                                i += 1
                        else:
                            document[i] = l
                            i += 1
                    else:
                        document[i], _ = loader.resolve_all(
                            val, base_url, file_base=file_base, checklinks=False)
                        i += 1
            except validate.ValidationException as v:
                _logger.warn("failed", exc_info=True)
                raise validate.ValidationException("(%s) (%s) Validation error in position %i:\n%s" % (
                    id(loader), file_base, i, validate.indent(six.text_type(v))))

            for identifer in loader.identity_links:
                if identifer in metadata:
                    if isinstance(metadata[identifer], (str, six.text_type)):
                        metadata[identifer] = loader.expand_url(
                            metadata[identifer], base_url, scoped_id=True)
                        loader.idx[metadata[identifer]] = document

        if checklinks:
            all_doc_ids={}  # type: Dict[Text, Text]
            self.validate_links(document, u"", all_doc_ids)

        return document, metadata

    def fetch(self, url, inject_ids=True):  # type: (Text, bool) -> Any
        if url in self.idx:
            return self.idx[url]
        try:
            text = self.fetch_text(url)
            if isinstance(text, bytes):
                textIO = StringIO(text.decode('utf-8'))
            else:
                textIO = StringIO(text)
            textIO.name = url    # type: ignore
            result = yaml.round_trip_load(textIO)
            add_lc_filename(result, url)
        except yaml.parser.ParserError as e:
            raise validate.ValidationException("Syntax error %s" % (e))
        if (isinstance(result, CommentedMap) and inject_ids
                and bool(self.identifiers)):
            for identifier in self.identifiers:
                if identifier not in result:
                    result[identifier] = url
                self.idx[self.expand_url(result[identifier], url)] = result
        else:
            self.idx[url] = result
        return result


    FieldType = TypeVar('FieldType', six.text_type, CommentedSeq, CommentedMap)

    def validate_scoped(self, field, link, docid):
        # type: (Text, Text, Text) -> Text
        split = urllib.parse.urlsplit(docid)
        sp = split.fragment.split(u"/")
        n = self.scoped_ref_fields[field]
        while n > 0 and len(sp) > 0:
            sp.pop()
            n -= 1
        tried = []
        while True:
            sp.append(link)
            url = urllib.parse.urlunsplit((
                split.scheme, split.netloc, split.path, split.query,
                u"/".join(sp)))
            tried.append(url)
            if url in self.idx:
                return url
            sp.pop()
            if len(sp) == 0:
                break
            sp.pop()
        raise validate.ValidationException(
            "Field `%s` references unknown identifier `%s`, tried %s" % (field, link, ", ".join(tried)))

    def validate_link(self, field, link, docid, all_doc_ids):
        # type: (Text, FieldType, Text, Dict[Text, Text]) -> FieldType
        if field in self.nolinkcheck:
            return link
        if isinstance(link, (str, six.text_type)):
            if field in self.vocab_fields:
                if (link not in self.vocab and link not in self.idx
                        and link not in self.rvocab):
                    if field in self.scoped_ref_fields:
                        return self.validate_scoped(field, link, docid)
                    elif not self.check_exists(link):
                        raise validate.ValidationException(
                            "Field `%s` contains undefined reference to `%s`" % (field, link))
            elif link not in self.idx and link not in self.rvocab:
                if field in self.scoped_ref_fields:
                    return self.validate_scoped(field, link, docid)
                elif not self.check_exists(link):
                    raise validate.ValidationException(
                        "Field `%s` contains undefined reference to `%s`"
                        % (field, link))
        elif isinstance(link, CommentedSeq):
            errors = []
            for n, i in enumerate(link):
                try:
                    link[n] = self.validate_link(field, i, docid, all_doc_ids)
                except validate.ValidationException as v:
                    errors.append(v)
            if bool(errors):
                raise validate.ValidationException(
                    "\n".join([six.text_type(e) for e in errors]))
        elif isinstance(link, CommentedMap):
            self.validate_links(link, docid, all_doc_ids)
        else:
            raise validate.ValidationException(
                "`%s` field is %s, expected string, list, or a dict."
                % (field, type(link).__name__))
        return link

    def getid(self, d):  # type: (Any) -> Optional[Text]
        if isinstance(d, dict):
            for i in self.identifiers:
                if i in d:
                    idd = d[i]
                    if isinstance(idd, (str, six.text_type)):
                        return idd
        return None

    def validate_links(self, document, base_url, all_doc_ids):
        # type: (Union[CommentedMap, CommentedSeq, Text, None], Text, Dict[Text, Text]) -> None
        docid = self.getid(document)
        if not docid:
            docid = base_url

        errors = []         # type: List[Exception]
        iterator = None     # type: Any
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            try:
                for d in self.url_fields:
                    sl = SourceLine(document, d, validate.ValidationException)
                    if d in document and d not in self.identity_links:
                        document[d] = self.validate_link(d, document[d], docid, all_doc_ids)
                for identifier in self.identifiers:  # validate that each id is defined uniquely
                    if identifier in document:
                        sl = SourceLine(document, identifier, validate.ValidationException)
                        if document[identifier] in all_doc_ids and sl.makeLead() != all_doc_ids[document[identifier]]:
                            raise validate.ValidationException(
                                "%s object %s `%s` previously defined" % (all_doc_ids[document[identifier]], identifier, relname(document[identifier]), ))
                        else:
                            all_doc_ids[document[identifier]] = sl.makeLead()
                            break
            except validate.ValidationException as v:
                errors.append(sl.makeError(six.text_type(v)))
            if hasattr(document, "iteritems"):
                iterator = six.iteritems(document)
            else:
                iterator = list(document.items())
        else:
            return

        for key, val in iterator:
            sl = SourceLine(document, key, validate.ValidationException)
            try:
                self.validate_links(val, docid, all_doc_ids)
            except validate.ValidationException as v:
                if key not in self.nolinkcheck:
                    docid2 = self.getid(val)
                    if docid2 is not None:
                        errors.append(sl.makeError("checking object `%s`\n%s"
                            % (relname(docid2), validate.indent(six.text_type(v)))))
                    else:
                        if isinstance(key, six.string_types):
                            errors.append(sl.makeError("checking field `%s`\n%s" % (
                                key, validate.indent(six.text_type(v)))))
                        else:
                            errors.append(sl.makeError("checking item\n%s" % (
                                validate.indent(six.text_type(v)))))
                else:
                    _logger.warn( validate.indent(six.text_type(v)))
        if bool(errors):
            if len(errors) > 1:
                raise validate.ValidationException(
                    u"\n".join([six.text_type(e) for e in errors]))
            else:
                raise errors[0]
        return


D = TypeVar('D', CommentedMap, ContextType)

def _copy_dict_without_key(from_dict, filtered_key):
    # type: (D, Any) -> D
    new_dict = copy.copy(from_dict)
    if filtered_key in new_dict:
        del new_dict[filtered_key]
    if isinstance(from_dict, CommentedMap):
        new_dict.lc.data = copy.copy(from_dict.lc.data)
        new_dict.lc.filename = from_dict.lc.filename
    return new_dict
