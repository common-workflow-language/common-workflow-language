import sys
import os
import json
import hashlib
import logging
import collections
import requests
import urlparse
import re
import copy
import ruamel.yaml as yaml
try:
    from ruamel.yaml import CSafeLoader as SafeLoader
except ImportError:
    from ruamel.yaml import SafeLoader  # type: ignore
from . import validate
import pprint
from StringIO import StringIO
from .aslist import aslist
from .flatten import flatten
import rdflib
from rdflib.namespace import RDF, RDFS, OWL
from rdflib.plugins.parsers.notation3 import BadSyntax
import xml.sax
from typing import (Any, AnyStr, Callable, cast, Dict, List, Iterable, Tuple,
         TypeVar, Union)

_logger = logging.getLogger("salad")

class NormDict(dict):

    def __init__(self, normalize=unicode):  # type: (type) -> None
        super(NormDict, self).__init__()
        self.normalize = normalize

    def __getitem__(self, key):
        return super(NormDict, self).__getitem__(self.normalize(key))

    def __setitem__(self, key, value):
        return super(NormDict, self).__setitem__(self.normalize(key), value)

    def __delitem__(self, key):
        return super(NormDict, self).__delitem__(self.normalize(key))

    def __contains__(self, key):
        return super(NormDict, self).__contains__(self.normalize(key))


def merge_properties(a, b):
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
                  cache=loader.cache)


class Loader(object):

    ContextType = Dict[unicode, Union[Dict, unicode, Iterable[unicode]]]
    DocumentType = TypeVar('DocumentType', List, Dict[unicode, Any])

    def __init__(self, ctx, schemagraph=None, foreign_properties=None,
                 idx=None, cache=None):
        # type: (Loader.ContextType, rdflib.Graph, Set[unicode], Dict[unicode, Union[List, Dict[unicode, Any], unicode]], Dict[unicode, Any]) -> None
        normalize = lambda url: urlparse.urlsplit(url).geturl()
        if idx is not None:
            self.idx = idx
        else:
            self.idx = NormDict(normalize)

        self.ctx = {}  # type: Loader.ContextType
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

        self.url_fields = None  # type: Set[unicode]
        self.scoped_ref_fields = None  # type: Dict[unicode, int]
        self.vocab_fields = None  # type: Set[unicode]
        self.identifiers = None  # type: Set[unicode]
        self.identity_links = None  # type: Set[unicode]
        self.standalone = None  # type: Set[unicode]
        self.nolinkcheck = None  # type: Set[unicode]
        self.vocab = {}  # type: Dict[unicode, unicode]
        self.rvocab = {}  # type: Dict[unicode, unicode]
        self.idmap = None  # type: Dict[unicode, Any]
        self.mapPredicate = None  # type: Dict[unicode, unicode]
        self.type_dsl_fields = None  # type: Set[unicode]

        self.add_context(ctx)

    def expand_url(self, url, base_url, scoped_id=False, vocab_term=False, scoped_ref=None):
        # type: (unicode, unicode, bool, bool, int) -> unicode
        if url in (u"@id", u"@type"):
            return url

        if vocab_term and url in self.vocab:
            return url

        if self.vocab and u":" in url:
            prefix = url.split(u":")[0]
            if prefix in self.vocab:
                url = self.vocab[prefix] + url[len(prefix) + 1:]

        split = urlparse.urlsplit(url)

        if split.scheme or url.startswith(u"$(") or url.startswith(u"${"):
            pass
        elif scoped_id and not split.fragment:
            splitbase = urlparse.urlsplit(base_url)
            frg = u""
            if splitbase.fragment:
                frg = splitbase.fragment + u"/" + split.path
            else:
                frg = split.path
            pt = splitbase.path if splitbase.path else "/"
            url = urlparse.urlunsplit(
                (splitbase.scheme, splitbase.netloc, pt, splitbase.query, frg))
        elif scoped_ref is not None and not split.fragment:
            pass
        else:
            url = urlparse.urljoin(base_url, url)

        if vocab_term and url in self.rvocab:
            return self.rvocab[url]
        else:
            return url

    def _add_properties(self, s):  # type: (unicode) -> None
        for _, _, rng in self.graph.triples((s, RDFS.range, None)):
            literal = ((unicode(rng).startswith(
                u"http://www.w3.org/2001/XMLSchema#") and
                not unicode(rng) == u"http://www.w3.org/2001/XMLSchema#anyURI")
                or unicode(rng) ==
                u"http://www.w3.org/2000/01/rdf-schema#Literal")
            if not literal:
                self.url_fields.add(unicode(s))
        self.foreign_properties.add(unicode(s))

    def add_namespaces(self, ns):  # type: (Dict[unicode, unicode]) -> None
        self.vocab.update(ns)

    def add_schemas(self, ns, base_url):
        # type: (Union[List[unicode], unicode], unicode) -> None
        for sch in aslist(ns):
            for fmt in ['xml', 'turtle', 'rdfa']:
                try:
                    self.graph.parse(urlparse.urljoin(base_url, sch),
                                     format=fmt)
                    break
                except xml.sax.SAXParseException:  # type: ignore
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
            self.idx[unicode(s)] = None

    def add_context(self, newcontext, baseuri=""):
        # type: (Loader.ContextType, unicode) -> None
        if self.vocab:
            raise validate.ValidationException(
                "Refreshing context that already has stuff in it")

        self.url_fields = set()
        self.scoped_ref_fields = {}
        self.vocab_fields = set()
        self.identifiers = set()
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
                self.identifiers.add(key)
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
            elif isinstance(value, basestring):
                self.vocab[key] = value

        for k, v in self.vocab.items():
            self.rvocab[self.expand_url(v, u"", scoped_id=False)] = k

        _logger.debug("identifiers is %s", self.identifiers)
        _logger.debug("identity_links is %s", self.identity_links)
        _logger.debug("url_fields is %s", self.url_fields)
        _logger.debug("vocab_fields is %s", self.vocab_fields)
        _logger.debug("vocab is %s", self.vocab)

    def resolve_ref(self, ref, base_url=None, checklinks=True):
        # type: (Union[Dict[unicode, Any], unicode], unicode, bool) -> Tuple[Union[List, Dict[unicode, Any], unicode], Dict[unicode, Any]]
        base_url = base_url or u'file://%s/' % os.path.abspath('.')

        obj = None  # type: Dict[unicode, Any]
        inc = False
        mixin = None

        # If `ref` is a dict, look for special directives.
        if isinstance(ref, dict):
            obj = ref
            if u"$import" in obj:
                if len(obj) == 1:
                    ref = obj[u"$import"]
                    obj = None
                else:
                    raise ValueError(
                        u"'$import' must be the only field in %s" % (str(obj)))
            elif u"$include" in obj:
                if len(obj) == 1:
                    ref = obj[u"$include"]
                    inc = True
                    obj = None
                else:
                    raise ValueError(
                        u"'$include' must be the only field in %s" % (str(obj)))
            elif u"$mixin" in obj:
                ref = obj[u"$mixin"]
                mixin = obj
                obj = None
            else:
                ref = None
                for identifier in self.identifiers:
                    if identifier in obj:
                        ref = obj[identifier]
                        break
                if not ref:
                    raise ValueError(
                        u"Object `%s` does not have identifier field in %s" % (obj, self.identifiers))

        if not isinstance(ref, (str, unicode)):
            raise ValueError(u"Must be string: `%s`" % str(ref))

        url = self.expand_url(ref, base_url, scoped_id=(obj is not None))

        # Has this reference been loaded already?
        if url in self.idx and (not mixin):
            return self.idx[url], {}

        # "$include" directive means load raw text
        if inc:
            return self.fetch_text(url), {}

        doc = None
        if obj:
            for identifier in self.identifiers:
                obj[identifier] = url
            doc_url = url
        else:
            # Load structured document
            doc_url, frg = urlparse.urldefrag(url)
            if doc_url in self.idx and (not mixin):
                # If the base document is in the index, it was already loaded,
                # so if we didn't find the reference earlier then it must not
                # exist.
                raise validate.ValidationException(
                    u"Reference `#%s` not found in file `%s`." % (frg, doc_url))
            doc = self.fetch(doc_url, inject_ids=(not mixin))

        # Recursively expand urls and resolve directives
        if mixin:
            doc = copy.deepcopy(doc)
            doc.update(mixin)
            del doc["$mixin"]
            url = None
            resolved_obj, metadata = self.resolve_all(
                doc, base_url, file_base=doc_url, checklinks=checklinks)
        else:
            resolved_obj, metadata = self.resolve_all(
                doc if doc else obj, doc_url, checklinks=checklinks)

        # Requested reference should be in the index now, otherwise it's a bad
        # reference
        if url is not None:
            if url in self.idx:
                resolved_obj = self.idx[url]
            else:
                raise RuntimeError("Reference `%s` is not in the index. "
                    "Index contains:\n  %s" % (url, "\n  ".join(self.idx)))

        if isinstance(resolved_obj, (dict)):
            if u"$graph" in resolved_obj:
                metadata = _copy_dict_without_key(resolved_obj, u"$graph")
                return resolved_obj[u"$graph"], metadata
            else:
                return resolved_obj, metadata
        else:
            return resolved_obj, metadata


    def _resolve_idmap(self, document, loader):
        # type: (Dict[unicode, Union[Dict[unicode, Dict[unicode, unicode]], List[Dict[unicode, Any]]]], Loader) -> None
        # Convert fields with mapSubject into lists
        # use mapPredicate if the mapped value isn't a dict.
        for idmapField in loader.idmap:
            if (idmapField in document):
                idmapFieldValue = document[idmapField]
                if (isinstance(idmapFieldValue, dict)
                        and "$import" not in idmapFieldValue
                        and "$include" not in idmapFieldValue):
                    ls = []
                    for k in sorted(idmapFieldValue.keys()):
                        val = idmapFieldValue[k]
                        v = None  # type: Dict[unicode, Any]
                        if not isinstance(val, dict):
                            if idmapField in loader.mapPredicate:
                                v = {loader.mapPredicate[idmapField]: val}
                            else:
                                raise validate.ValidationException(
                                    "mapSubject '%s' value '%s' is not a dict"
                                    "and does not have a mapPredicate", k, v)
                        else:
                            v = val
                        v[loader.idmap[idmapField]] = k
                        ls.append(v)
                    document[idmapField] = ls

    typeDSLregex = re.compile(ur"^([^[?]+)(\[\])?(\?)?$")

    def _type_dsl(self, t):
        # type: (Union[unicode, Dict, List]) -> Union[unicode, Dict[unicode, unicode], List[Union[unicode, Dict[unicode, unicode]]]]
        if not isinstance(t, (str, unicode)):
            return t

        m = Loader.typeDSLregex.match(t)
        if not m:
            return t
        first = m.group(1)
        second = third = None
        if m.group(2):
            second = {u"type": u"array",
                 u"items": first}
        if m.group(3):
            third = [u"null", second or first]
        return third or second or first

    def _resolve_type_dsl(self, document, loader):
        # type: (Dict[unicode, Union[unicode, Dict[unicode, unicode], List]], Loader) -> None
        for d in loader.type_dsl_fields:
            if d in document:
                datum = document[d]
                if isinstance(datum, (str, unicode)):
                    document[d] = self._type_dsl(datum)
                elif isinstance(datum, list):
                    document[d] = [self._type_dsl(t) for t in datum]
                datum2 = document[d]
                if isinstance(datum2, list):
                    document[d] = flatten(datum2)
                    seen = []  # type: List[unicode]
                    uniq = []
                    for item in document[d]:
                        if item not in seen:
                            uniq.append(item)
                            seen.append(item)
                    document[d] = uniq

    def _resolve_identifier(self, document, loader, base_url):
        # type: (Dict[unicode, unicode], Loader, unicode) -> unicode
        # Expand identifier field (usually 'id') to resolve scope
        for identifer in loader.identifiers:
            if identifer in document:
                if isinstance(document[identifer], basestring):
                    document[identifer] = loader.expand_url(
                        document[identifer], base_url, scoped_id=True)
                    if (document[identifer] not in loader.idx
                            or isinstance(
                                loader.idx[document[identifer]], basestring)):
                        loader.idx[document[identifer]] = document
                    base_url = document[identifer]
                else:
                    raise validate.ValidationException(
                        "identifier field '%s' must be a string"
                        % (document[identifer]))
        return base_url

    def _resolve_identity(self, document, loader, base_url):
        # type: (Dict[unicode, List[unicode]], Loader, unicode) -> None
        # Resolve scope for identity fields (fields where the value is the
        # identity of a standalone node, such as enum symbols)
        for identifer in loader.identity_links:
            if identifer in document and isinstance(document[identifer], list):
                for n, v in enumerate(document[identifer]):
                    if isinstance(document[identifer][n], basestring):
                        document[identifer][n] = loader.expand_url(
                            document[identifer][n], base_url, scoped_id=True)
                        if document[identifer][n] not in loader.idx:
                            loader.idx[document[identifer][
                                n]] = document[identifer][n]

    def _normalize_fields(self, document, loader):
        # type: (Dict[unicode, unicode], Loader) -> None
        # Normalize fields which are prefixed or full URIn to vocabulary terms
        for d in document:
            d2 = loader.expand_url(d, u"", scoped_id=False, vocab_term=True)
            if d != d2:
                document[d2] = document[d]
                del document[d]

    def _resolve_uris(self, document, loader, base_url):
        # type: (Dict[unicode, Union[unicode, List[unicode]]], Loader, unicode) -> None
        # Resolve remaining URLs based on document base
        for d in loader.url_fields:
            if d in document:
                datum = document[d]
                if isinstance(datum, (str, unicode)):
                    document[d] = loader.expand_url(
                        datum, base_url, scoped_id=False,
                        vocab_term=(d in loader.vocab_fields),
                        scoped_ref=self.scoped_ref_fields.get(d))
                elif isinstance(datum, list):
                    document[d] = [
                        loader.expand_url(
                            url, base_url, scoped_id=False,
                            vocab_term=(d in loader.vocab_fields),
                            scoped_ref=self.scoped_ref_fields.get(d))
                        if isinstance(url, (str, unicode))
                        else url for url in datum]


    def resolve_all(self, document, base_url, file_base=None, checklinks=True):
        # type: (DocumentType, unicode, unicode, bool) -> Tuple[Union[List, Dict[unicode, Any], unicode], Dict[unicode, Any]]
        loader = self
        metadata = {}  # type: Dict[unicode, Any]
        if file_base is None:
            file_base = base_url

        if isinstance(document, dict):
            # Handle $import and $include
            if (u'$import' in document or u'$include' in document):
                return self.resolve_ref(document, base_url=file_base, checklinks=checklinks)
            elif u'$mixin' in document:
                return self.resolve_ref(document, base_url=base_url, checklinks=checklinks)
        elif isinstance(document, list):
            pass
        else:
            return (document, metadata)

        newctx = None  # type: Loader
        if isinstance(document, dict):
            # Handle $base, $profile, $namespaces, $schemas and $graph
            if u"$base" in document:
                base_url = document[u"$base"]

            if u"$profile" in document:
                if not newctx:
                    newctx = SubLoader(self)
                prof = self.fetch(document[u"$profile"])
                newctx.add_namespaces(document.get(u"$namespaces", {}))
                newctx.add_schemas(document.get(
                    u"$schemas", []), document[u"$profile"])

            if u"$namespaces" in document:
                if not newctx:
                    newctx = SubLoader(self)
                newctx.add_namespaces(document[u"$namespaces"])

            if u"$schemas" in document:
                if not newctx:
                    newctx = SubLoader(self)
                newctx.add_schemas(document[u"$schemas"], file_base)

            if newctx:
                loader = newctx

            if u"$graph" in document:
                metadata = _copy_dict_without_key(document, u"$graph")
                document = document[u"$graph"]
                resolved_metadata = loader.resolve_all(metadata, base_url,
                        file_base=file_base, checklinks=False)[0]
                if isinstance(resolved_metadata, dict):
                    metadata = resolved_metadata
                else:
                    raise validate.ValidationException(
                        "Validation error, metadata must be dict: %s"
                        % (resolved_metadata))

        if isinstance(document, dict):
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
                _logger.warn("loader is %s", id(loader), exc_info=v)
                raise validate.ValidationException("(%s) (%s) Validation error in field %s:\n%s" % (
                    id(loader), file_base, key, validate.indent(str(v))))

        elif isinstance(document, list):
            i = 0
            try:
                while i < len(document):
                    val = document[i]
                    if isinstance(val, dict) and (u"$import" in val or u"$mixin" in val):
                        l, _ = loader.resolve_ref(val, base_url=file_base, checklinks=False)
                        if isinstance(l, list):  # never true?
                            del document[i]
                            for item in aslist(l):
                                document.insert(i, item)
                                i += 1
                        else:
                            document[i] = l
                            i += 1
                    else:
                        document[i], _ = loader.resolve_all(
                            val, base_url, file_base=file_base, checklinks=False)
                        i += 1
            except validate.ValidationException as v:
                _logger.warn("failed", exc_info=v)
                raise validate.ValidationException("(%s) (%s) Validation error in position %i:\n%s" % (
                    id(loader), file_base, i, validate.indent(str(v))))

            for identifer in loader.identity_links:
                if identifer in metadata:
                    if isinstance(metadata[identifer], (str, unicode)):
                        metadata[identifer] = loader.expand_url(
                            metadata[identifer], base_url, scoped_id=True)
                        loader.idx[metadata[identifer]] = document

        if checklinks:
            document = self.validate_links(document, u"")

        return document, metadata

    def fetch_text(self, url):
        # type: (unicode) -> unicode
        if url in self.cache:
            return self.cache[url]

        split = urlparse.urlsplit(url)
        scheme, path = split.scheme, split.path

        if scheme in [u'http', u'https'] and requests:
            try:
                resp = requests.get(url)
                resp.raise_for_status()
            except Exception as e:
                raise RuntimeError(url, e)
            return resp.text
        elif scheme == 'file':
            try:
                with open(path) as fp:
                    read = fp.read()
                if hasattr(read, "decode"):
                    return read.decode("utf-8")
                else:
                    return read
            except (OSError, IOError) as e:
                raise RuntimeError('Error reading %s %s' % (url, e))
        else:
            raise ValueError('Unsupported scheme in url: %s' % url)

    def fetch(self, url, inject_ids=True):  # type: (unicode, bool) -> Any
        if url in self.idx:
            return self.idx[url]
        try:
            text = self.fetch_text(url)
            if isinstance(text, bytes):
                textIO = StringIO(text.decode('utf-8'))
            else:
                textIO = StringIO(text)
            textIO.name = url  # type: ignore
            result = yaml.load(textIO, Loader=SafeLoader)
        except yaml.parser.ParserError as e:  # type: ignore
            raise validate.ValidationException("Syntax error %s" % (e))
        if isinstance(result, dict) and inject_ids and self.identifiers:
            for identifier in self.identifiers:
                if identifier not in result:
                    result[identifier] = url
                self.idx[self.expand_url(result[identifier], url)] = result
        else:
            self.idx[url] = result
        return result

    def check_file(self, fn):  # type: (unicode) -> bool
        if fn.startswith("file://"):
            u = urlparse.urlsplit(fn)
            return os.path.exists(u.path)
        else:
            return False

    FieldType = TypeVar('FieldType', unicode, List[unicode], Dict[unicode, Any])

    def validate_scoped(self, field, link, docid):
        # type: (unicode, unicode, unicode) -> unicode
        split = urlparse.urlsplit(docid)
        sp = split.fragment.split(u"/")
        n = self.scoped_ref_fields[field]
        while n > 0 and len(sp) > 0:
            sp.pop()
            n -= 1
        tried = []
        while True:
            sp.append(link)
            url = urlparse.urlunsplit((
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
            "Field `%s` contains undefined reference to `%s`, tried %s" % (field, link, tried))

    def validate_link(self, field, link, docid):
        # type: (unicode, FieldType, unicode) -> FieldType
        if field in self.nolinkcheck:
            return link
        if isinstance(link, (str, unicode)):
            if field in self.vocab_fields:
                if link not in self.vocab and link not in self.idx and link not in self.rvocab:
                    if field in self.scoped_ref_fields:
                        return self.validate_scoped(field, link, docid)
                    elif not self.check_file(link):
                        raise validate.ValidationException(
                            "Field `%s` contains undefined reference to `%s`" % (field, link))
            elif link not in self.idx and link not in self.rvocab:
                if field in self.scoped_ref_fields:
                    return self.validate_scoped(field, link, docid)
                elif not self.check_file(link):
                    raise validate.ValidationException(
                        "Field `%s` contains undefined reference to `%s`" % (field, link))
        elif isinstance(link, list):
            errors = []
            for n, i in enumerate(link):
                try:
                    link[n] = self.validate_link(field, i, docid)
                except validate.ValidationException as v:
                    errors.append(v)
            if errors:
                raise validate.ValidationException(
                    "\n".join([str(e) for e in errors]))
        elif isinstance(link, dict):
            self.validate_links(link, docid)
        else:
            raise validate.ValidationException("Link must be a str, unicode, "
                                               "list, or a dict.")
        return link

    def getid(self, d):  # type: (Any) -> unicode
        if isinstance(d, dict):
            for i in self.identifiers:
                if i in d:
                    if isinstance(d[i], (str, unicode)):
                        return d[i]
        return None

    def validate_links(self, document, base_url):
        # type: (DocumentType, unicode) -> DocumentType
        docid = self.getid(document)
        if not docid:
            docid = base_url

        errors = []
        iterator = None  # type: Any
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            try:
                for d in self.url_fields:
                    if d in document and d not in self.identity_links:
                        document[d] = self.validate_link(d, document[d], docid)
            except validate.ValidationException as v:
                errors.append(v)
            if hasattr(document, "iteritems"):
                iterator = document.iteritems()
            else:
                iterator = document.items()
        else:
            return document

        for key, val in iterator:
            try:
                document[key] = self.validate_links(val, docid)  # type: ignore
            except validate.ValidationException as v:
                if key not in self.nolinkcheck:
                    docid2 = self.getid(val)
                    if docid2:
                        errors.append(validate.ValidationException(
                            "While checking object `%s`\n%s" % (docid2, validate.indent(str(v)))))
                    else:
                        if isinstance(key, basestring):
                            errors.append(validate.ValidationException(
                                "While checking field `%s`\n%s" % (key, validate.indent(str(v)))))
                        else:
                            errors.append(validate.ValidationException(
                                "While checking position %s\n%s" % (key, validate.indent(str(v)))))

        if errors:
            if len(errors) > 1:
                raise validate.ValidationException(
                    "\n".join([str(e) for e in errors]))
            else:
                raise errors[0]
        return document


def _copy_dict_without_key(from_dict, filtered_key):
    # type: (Dict, Any) -> Dict
    new_dict = {}
    for key, value in from_dict.items():
        if key != filtered_key:
            new_dict[key] = value
    return new_dict
