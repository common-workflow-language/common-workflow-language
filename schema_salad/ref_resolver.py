import sys
import os
import json
import hashlib
import logging
import collections
import requests
import urlparse
import ruamel.yaml as yaml
try:
    from ruamel.yaml import CSafeLoader as SafeLoader
except ImportError:
    from ruamel.yaml import SafeLoader  # type: ignore
from . import validate
import pprint
from StringIO import StringIO
from .aslist import aslist
import rdflib
from rdflib.namespace import RDF, RDFS, OWL
import xml.sax
from typing import cast, Union, Tuple, Dict, Any, Callable, Iterable

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

    ContextType = Dict[str, Union[Dict, str, Iterable[str]]]

    def __init__(self, ctx, schemagraph=None, foreign_properties=None,
                 idx=None, cache=None):
        # type: (Loader.ContextType, rdflib.Graph, Set[str], Dict[unicode, Any], Dict[unicode, Any]) -> None
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

        self.url_fields = None  # type: Set[str]
        self.vocab_fields = None  # type: Set[str]
        self.identifiers = None  # type: Set[str]
        self.identity_links = None  # type: Set[str]
        self.standalone = None  # type: Set[str]
        self.nolinkcheck = None  # type: Set[str]
        self.vocab = {}  # type: Dict[unicode, Any]
        self.rvocab = {}  # type: Dict[unicode, Any]
        self.idmap = None  # type: Dict[unicode, Any]
        self.mapPredicate = None  # type: Dict[unicode, Any]

        self.add_context(ctx)

    def expand_url(self, url, base_url, scoped=False, vocab_term=False):
        # type: (Union[str, unicode], Union[str, unicode], bool, bool) -> Union[str, unicode]
        if url in ("@id", "@type"):
            return url

        if vocab_term and url in self.vocab:
            return url

        if self.vocab and ":" in url:
            prefix = url.split(":")[0]
            if prefix in self.vocab:
                url = self.vocab[prefix] + url[len(prefix) + 1:]

        split = urlparse.urlsplit(url)

        if split.scheme or url.startswith("$(") or url.startswith("${"):
            pass
        elif scoped and not split.fragment:
            splitbase = urlparse.urlsplit(base_url)
            frg = ""
            if splitbase.fragment:
                frg = splitbase.fragment + "/" + split.path
            else:
                frg = split.path
            url = urlparse.urlunsplit(
                (splitbase.scheme, splitbase.netloc, splitbase.path, splitbase.query, frg))
        else:
            url = urlparse.urljoin(base_url, url)

        if vocab_term and url in self.rvocab:
            return self.rvocab[url]
        else:
            return url

    def _add_properties(self, s):  # type: (str) -> None
        for _, _, rng in self.graph.triples((s, RDFS.range, None)):
            literal = ((str(rng).startswith("http://www.w3.org/2001/XMLSchema#") and not str(rng) == "http://www.w3.org/2001/XMLSchema#anyURI") or
                       str(rng) == "http://www.w3.org/2000/01/rdf-schema#Literal")
            if not literal:
                self.url_fields.add(str(s))
        self.foreign_properties.add(str(s))

    def add_namespaces(self, ns):  # type: (Dict[unicode, Any]) -> None
        self.vocab.update(ns)

    def add_schemas(self, ns, base_url):
        # type: (Dict[str, Any], Union[str, unicode]) -> None
        for sch in aslist(ns):
            for fmt in ['xml', 'turtle', 'rdfa']:
                try:
                    self.graph.parse(urlparse.urljoin(base_url, sch),
                                     format=fmt)
                    break
                except xml.sax.SAXParseException:  # type: ignore
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
            self.idx[str(s)] = True

    def add_context(self, newcontext, baseuri=""):
        # type: (Loader.ContextType, str) -> None
        if self.vocab:
            raise validate.ValidationException(
                "Refreshing context that already has stuff in it")

        self.url_fields = set()
        self.vocab_fields = set()
        self.identifiers = set()
        self.identity_links = set()
        self.standalone = set()
        self.nolinkcheck = set()
        self.idmap = {}
        self.mapPredicate = {}
        self.vocab = {}
        self.rvocab = {}

        self.ctx.update(_copy_dict_without_key(newcontext, "@context"))

        _logger.debug("ctx is %s", self.ctx)

        for key, value in self.ctx.items():
            if value == "@id":
                self.identifiers.add(key)
                self.identity_links.add(key)
            elif isinstance(value, dict) and value.get("@type") == "@id":
                self.url_fields.add(key)
                if value.get("identity", False):
                    self.identity_links.add(key)
            elif isinstance(value, dict) and value.get("@type") == "@vocab":
                self.url_fields.add(key)
                self.vocab_fields.add(key)

            if isinstance(value, dict) and value.get("noLinkCheck"):
                self.nolinkcheck.add(key)

            if isinstance(value, dict) and value.get("mapSubject"):
                self.idmap[key] = value["mapSubject"]

            if isinstance(value, dict) and value.get("mapPredicate"):
                self.mapPredicate[key] = value["mapPredicate"]

            if isinstance(value, dict) and "@id" in value:
                self.vocab[key] = value["@id"]
            elif isinstance(value, basestring):
                self.vocab[key] = value

        for k, v in self.vocab.items():
            self.rvocab[self.expand_url(v, "", scoped=False)] = k

        _logger.debug("identifiers is %s", self.identifiers)
        _logger.debug("identity_links is %s", self.identity_links)
        _logger.debug("url_fields is %s", self.url_fields)
        _logger.debug("vocab_fields is %s", self.vocab_fields)
        _logger.debug("vocab is %s", self.vocab)

    def resolve_ref(self, ref, base_url=None):
        # type: (Union[Dict[str, Any], str, unicode], Union[str, unicode]) -> Tuple[Union[Dict[str, Any], str, unicode], Dict[str, Any]]
        base_url = base_url or 'file://%s/' % os.path.abspath('.')

        obj = None  # type: Dict[str, Any]
        inc = False

        # If `ref` is a dict, look for special directives.
        if isinstance(ref, dict):
            obj = ref
            if "$import" in ref:
                if len(obj) == 1:
                    ref = obj["$import"]
                    obj = None
                else:
                    raise ValueError(
                        "'$import' must be the only field in %s" % (str(obj)))
            elif "$include" in obj:
                if len(obj) == 1:
                    ref = obj["$include"]
                    inc = True
                    obj = None
                else:
                    raise ValueError(
                        "'$include' must be the only field in %s" % (str(obj)))
            else:
                ref = None
                for identifier in self.identifiers:
                    if identifier in obj:
                        ref = obj[identifier]
                        break
                if not ref:
                    raise ValueError(
                        "Object `%s` does not have identifier field in %s" % (obj, self.identifiers))

        if not isinstance(ref, (str, unicode)):
            raise ValueError("Must be string: `%s`" % str(ref))

        url = self.expand_url(cast(  # bug in mypy 0.3.1, fixed in 0.4-dev
            Union[str, unicode], ref), base_url,
            scoped=(obj is not None))

        # Has this reference been loaded already?
        if url in self.idx:
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
            if doc_url in self.idx:
                raise validate.ValidationException(
                    "Reference `#%s` not found in file `%s`." % (frg, doc_url))
            doc = self.fetch(doc_url)

        # Recursively expand urls and resolve directives
        obj, metadata = self.resolve_all(doc if doc else obj, doc_url)

        # Requested reference should be in the index now, otherwise it's a bad
        # reference
        if url is not None:
            if url in self.idx:
                obj = self.idx[url]
            else:
                raise RuntimeError("Reference `%s` is not in the index.  Index contains:\n  %s" % (
                    url, "\n  ".join(self.idx)))

        try:
            if "$graph" in obj:
                metadata = _copy_dict_without_key(obj, "$graph")
                obj = obj["$graph"]
                return obj, metadata
            else:
                return obj, metadata
        except TypeError:
            return obj, metadata

    def resolve_all(self, document, base_url, file_base=None):
        # type: (Any, Union[str, unicode], Union[str, unicode]) -> Tuple[Any, Dict[str, str]]
        loader = self
        metadata = {}  # type: Dict[str, Any]
        if file_base is None:
            file_base = base_url

        if isinstance(document, dict):
            # Handle $import and $include
            if ('$import' in document or '$include' in document):
                return self.resolve_ref(document, file_base)
        elif isinstance(document, list):
            pass
        else:
            return (document, metadata)

        newctx = None
        if isinstance(document, dict):
            # Handle $base, $profile, $namespaces, $schemas and $graph
            if "$base" in document:
                base_url = document["$base"]

            if "$profile" in document:
                if not newctx:
                    newctx = SubLoader(self)
                prof = self.fetch(document["$profile"])
                newctx.add_namespaces(document.get("$namespaces", {}))
                newctx.add_schemas(document.get(
                    "$schemas", []), document["$profile"])

            if "$namespaces" in document:
                if not newctx:
                    newctx = SubLoader(self)
                newctx.add_namespaces(document["$namespaces"])

            if "$schemas" in document:
                if not newctx:
                    newctx = SubLoader(self)
                newctx.add_schemas(document["$schemas"], file_base)

            if newctx:
                loader = newctx

            if "$graph" in document:
                metadata = _copy_dict_without_key(document, "$graph")
                document = document["$graph"]
                metadata, _ = loader.resolve_all(metadata, base_url, file_base)

        if isinstance(document, dict):
            for idmapField in loader.idmap:
                if (idmapField in document and isinstance(document[idmapField], dict) and
                    "$import" not in document[idmapField] and
                    "$include" not in document[idmapField]):
                    ls = []
                    for k, v in document[idmapField].items():
                        if not isinstance(v, dict):
                            if idmapField in loader.mapPredicate:
                                v = {loader.mapPredicate[idmapField]: v}
                            else:
                                raise validate.ValidationException(
                                    "mapSubject '%s' value '%s' is not a dict and does not have a mapPredicate", k, v)
                        v[loader.idmap[idmapField]] = k
                        ls.append(v)
                    document[idmapField] = ls

            for identifer in loader.identifiers:
                if identifer in document:
                    if isinstance(document[identifer], basestring):
                        document[identifer] = loader.expand_url(
                            document[identifer], base_url, scoped=True)
                        if document[identifer] not in loader.idx or isinstance(loader.idx[document[identifer]], basestring):
                            loader.idx[document[identifer]] = document
                        base_url = document[identifer]
                    else:
                        raise validate.ValidationException(
                            "identifier field '%s' must be a string" % (document[identifer]))

            for identifer in loader.identity_links:
                if identifer in document and isinstance(document[identifer], list):
                    for n, v in enumerate(document[identifer]):
                        if isinstance(document[identifer][n], basestring):
                            document[identifer][n] = loader.expand_url(
                                document[identifer][n], base_url, scoped=True)
                            if document[identifer][n] not in loader.idx:
                                loader.idx[document[identifer][
                                    n]] = document[identifer][n]

            for d in document:
                d2 = loader.expand_url(d, "", scoped=False, vocab_term=True)
                if d != d2:
                    document[d2] = document[d]
                    del document[d]

            for d in loader.url_fields:
                if d in document:
                    if isinstance(document[d], basestring):
                        document[d] = loader.expand_url(
                            document[d], base_url, scoped=False, vocab_term=(d in loader.vocab_fields))
                    elif isinstance(document[d], list):
                        document[d] = [
                            loader.expand_url(
                                url, base_url, scoped=False,
                                vocab_term=(d in loader.vocab_fields))
                            if isinstance(url, (str, unicode))
                            else url for url in document[d]]

            try:
                for key, val in document.items():
                    document[key], _ = loader.resolve_all(
                        val, base_url, file_base)
            except validate.ValidationException as v:
                _logger.debug("loader is %s", id(loader))
                raise validate.ValidationException("(%s) (%s) Validation error in field %s:\n%s" % (
                    id(loader), file_base, key, validate.indent(str(v))))

        elif isinstance(document, list):
            i = 0
            try:
                while i < len(document):
                    val = document[i]
                    if isinstance(val, dict) and "$import" in val:
                        l, _ = loader.resolve_ref(val, file_base)
                        if isinstance(l, list):
                            del document[i]
                            for item in aslist(l):
                                document.insert(i, item)
                                i += 1
                        else:
                            document[i] = l
                            i += 1
                    else:
                        document[i], _ = loader.resolve_all(
                            val, base_url, file_base)
                        i += 1
            except validate.ValidationException as v:
                raise validate.ValidationException("(%s) (%s) Validation error in position %i:\n%s" % (
                    id(loader), file_base, i, validate.indent(str(v))))

            for identifer in loader.identity_links:
                if identifer in metadata:
                    if isinstance(metadata[identifer], (str, unicode)):
                        metadata[identifer] = loader.expand_url(
                            metadata[identifer], base_url, scoped=True)
                        loader.idx[metadata[identifer]] = document

        return document, metadata

    def fetch_text(self, url):
        # type: (Union[str, unicode]) -> Union[str, unicode]
        if url in self.cache:
            return self.cache[url]

        split = urlparse.urlsplit(url)
        scheme, path = split.scheme, split.path

        if scheme in ['http', 'https'] and requests:
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

    def fetch(self, url):  # type: (Union[str, unicode]) -> Any
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
        if isinstance(result, dict) and self.identifiers:
            for identifier in self.identifiers:
                if identifier not in result:
                    result[identifier] = url
                self.idx[self.expand_url(result[identifier], url)] = result
        else:
            self.idx[url] = result
        return result

    def check_file(self, fn):  # type: (Union[str, unicode]) -> bool
        if fn.startswith("file://"):
            u = urlparse.urlsplit(fn)
            return os.path.exists(u.path)
        else:
            return False

    def validate_link(self, field, link):
        # type: (str, Union[str, unicode, List[str], Dict[str, Any]]) -> bool
        if field in self.nolinkcheck:
            return True
        if isinstance(link, (str, unicode)):
            if field in self.vocab_fields:
                if link not in self.vocab and link not in self.idx and link not in self.rvocab:
                    if not self.check_file(cast(  # bug in mypy 0.3.1
                            Union[str, unicode], link)):  # fixed in mypy 0.4-dev
                        raise validate.ValidationException(
                            "Field `%s` contains undefined reference to `%s`" % (field, link))
            elif link not in self.idx and link not in self.rvocab:
                if not self.check_file(cast(  # bug in mypy 0.3.1
                        Union[str, unicode], link)):  # fixed in mypy 0.4-dev
                    raise validate.ValidationException(
                        "Field `%s` contains undefined reference to `%s`" % (field, link))
        elif isinstance(link, list):
            errors = []
            for i in link:
                try:
                    self.validate_link(field, i)
                except validate.ValidationException as v:
                    errors.append(v)
            if errors:
                raise validate.ValidationException(
                    "\n".join([str(e) for e in errors]))
        elif isinstance(link, dict):
            self.validate_links(link)
        else:
            raise validate.ValidationException("Link must be a str, unicode, "
                                               "list, or a dict.")
        return True

    def getid(self, d):  # type: (Any) -> Union[basestring, None]
        if isinstance(d, dict):
            for i in self.identifiers:
                if i in d:
                    if isinstance(d[i], basestring):
                        return d[i]
        return None

    def validate_links(self, document):  # type: (Any) -> None
        docid = self.getid(document)
        if docid is None:
            docid = ""

        errors = []
        iterator = None  # type: Any
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            try:
                for d in self.url_fields:
                    if d not in self.identity_links and d in document:
                        self.validate_link(d, document[d])
            except validate.ValidationException as v:
                errors.append(v)
            if hasattr(document, "iteritems"):
                iterator = document.iteritems()
            else:
                iterator = document.items()
        else:
            return

        for key, val in iterator:
            try:
                self.validate_links(val)
            except validate.ValidationException as v:
                if key not in self.nolinkcheck:
                    docid = self.getid(val)
                    if docid:
                        errors.append(validate.ValidationException(
                            "While checking object `%s`\n%s" % (docid, validate.indent(str(v)))))
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
        return


def _copy_dict_without_key(from_dict, filtered_key):
    # type: (Dict, Any) -> Dict
    new_dict = {}
    for key, value in from_dict.items():
        if key != filtered_key:
            new_dict[key] = value
    return new_dict
