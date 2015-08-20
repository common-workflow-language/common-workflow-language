import os
import json
import hashlib
import logging
import collections
import requests
import urlparse
import yaml
import validate

_logger = logging.getLogger("salad")

class NormDict(dict):
    def __init__(self, normalize=unicode):
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


def expand_url(url, base_url, scoped=False, vocab=None):
    if vocab and ":" in url:
        prefix = url.split(":")[0]
        if prefix in vocab:
            return vocab[prefix] + url[len(prefix)+1:]

    split = urlparse.urlsplit(url)

    if split.scheme:
        return url
    elif scoped and not split.fragment:
        splitbase = urlparse.urlsplit(base_url)
        frg = ""
        if splitbase.fragment:
            frg = splitbase.fragment + "/" + split.path
        else:
            frg = split.path
        return urlparse.urlunsplit((splitbase.scheme, splitbase.netloc, splitbase.path, splitbase.query, frg))
    elif vocab and url in vocab:
        return vocab[url]
    else:
        return urlparse.urljoin(base_url, url)

class Loader(object):
    def __init__(self, ctx):
        normalize = lambda url: urlparse.urlsplit(url).geturl()
        self.idx = NormDict(normalize)
        self.ctx = {}
        self.add_context(ctx)

    def add_context(self, newcontext):
        self.url_fields = []
        self.checked_urls = []
        self.vocab_fields = []
        self.identifiers = []
        self.vocab = {}

        self.ctx.update(newcontext)

        _logger.debug("ctx is %s", self.ctx)

        for c in self.ctx:
            if self.ctx[c] == "@id":
                self.identifiers.append(c)
            elif isinstance(self.ctx[c], dict) and self.ctx[c].get("@type") == "@id":
                self.url_fields.append(c)
                if self.ctx[c].get("checkedURI", True):
                    self.checked_urls.append(c)
            elif isinstance(self.ctx[c], dict) and self.ctx[c].get("@type") == "@vocab":
                self.url_fields.append(c)
                self.vocab_fields.append(c)

            if isinstance(self.ctx[c], dict) and "@id" in self.ctx[c]:
                self.vocab[c] = self.ctx[c]["@id"]
            elif isinstance(self.ctx[c], basestring):
                self.vocab[c] = self.ctx[c]

        _logger.debug("identifiers is %s", self.identifiers)
        _logger.debug("url_fields is %s", self.url_fields)
        _logger.debug("checked_urls is %s", self.checked_urls)
        _logger.debug("vocab_fields is %s", self.vocab_fields)
        _logger.debug("vocab is %s", self.vocab)


    def resolve_ref(self, ref, base_url=None):
        base_url = base_url or 'file://%s/' % os.path.abspath('.')

        obj = None

        # If `ref` is a dict, look for special directives.
        if isinstance(ref, dict):
            obj = ref
            if "import" in ref:
                if len(obj) == 1:
                    ref = obj["import"]
                    obj = None
                else:
                    raise ValueError("'import' must be the only field in %s" % (str(obj)))
            elif "include" in obj:
                if len(obj) == 1:
                    ref = obj["include"]
                else:
                    raise ValueError("'include' must be the only field in %s" % (str(obj)))
            else:
                ref = None
                for identifier in self.identifiers:
                    if identifier in obj:
                        ref = obj[identifier]
                        break
                if not ref:
                    raise ValueError("Object `%s` does not have `id` field" % obj)

        if not isinstance(ref, basestring):
            raise ValueError("Must be string: `%s`" % str(ref))

        url = expand_url(ref, base_url, scoped=(obj is not None))

        # Has this reference been loaded already?
        if url in self.idx:
            return self.idx[url]

        # "include" directive means load raw text
        if obj and "include" in obj:
            return self.fetch_text(url)

        if obj:
            for identifier in self.identifiers:
                obj[identifier] = url
            self.idx[url] = obj
        else:
            # Load structured document
            doc_url, frg = urlparse.urldefrag(url)
            if doc_url in self.idx:
                raise validate.ValidationException("Reference `#%s` not found in file `%s`." % (frg, doc_url))
            obj = self.fetch(doc_url)

        # Recursively expand urls and resolve directives
        obj = self.resolve_all(obj, url)

        # Requested reference should be in the index now, otherwise it's a bad reference
        if self.idx.get(url) is not None:
            #return self.idx[url]
            return obj
        else:
            raise RuntimeError("Reference `%s` is not in the index.  Index contains:\n  %s" % (url, "\n  ".join(self.idx)))

    def resolve_all(self, document, base_url):
        loader = self

        if isinstance(document, dict):
            inc = 'include' in document
            if  'import' in document or 'include' in document:
                document = self.resolve_ref(document, base_url)
            else:
                for identifer in self.identifiers:
                    if identifer in document:
                        document = self.resolve_ref(document, base_url)
                        break
            if inc:
                return document

            if "@context" in document:
                loader = Loader(self.ctx)
                loader.idx = self.idx
                loader.add_context(document["@context"])
                if "@base" in loader.ctx:
                    base_url = loader.ctx["@base"]
                if "@graph" in document:
                    document = document["@graph"]
        elif isinstance(document, list):
            pass
        else:
            return document

        if isinstance(document, dict):
            for d in loader.url_fields:
                vocab = loader.vocab if d in loader.vocab_fields else None
                if d in document:
                    if isinstance(document[d], basestring):
                        document[d] = expand_url(document[d], base_url, False, vocab)
                    elif isinstance(document[d], list):
                        document[d] = [expand_url(url, base_url, False, vocab) if isinstance(url, basestring) else url for url in document[d] ]
            iterator = document.iteritems()
        elif isinstance(document, list):
            iterator = enumerate(document)
        else:
            return document

        for key, val in iterator:
            try:
                document[key] = loader.resolve_all(val, base_url)
            except validate.ValidationException as v:
                if isinstance(key, basestring):
                    raise validate.ValidationException("Validation error in field %s:\n%s" % (key, validate.indent(str(v))))
                else:
                    raise validate.ValidationException("Validation error in position %i:\n%s" % (key, validate.indent(str(v))))

        return document

    def fetch_text(self, url):
        split = urlparse.urlsplit(url)
        scheme, path = split.scheme, split.path

        if scheme in ['http', 'https'] and requests:
            resp = requests.get(url)
            try:
                resp.raise_for_status()
            except Exception as e:
                raise RuntimeError(url, e)
            return resp.text
        elif scheme == 'file':
            try:
                with open(path) as fp:
                    return fp.read().decode("utf-8")
            except (OSError, IOError) as e:
                raise RuntimeError('Error reading %s %s' % (url, e))
        else:
            raise ValueError('Unsupported scheme in url: %s' % url)

    def fetch(self, url):
        if url in self.idx:
            return self.idx[url]
        try:
            result = yaml.load(self.fetch_text(url))
        except yaml.parser.ParserError as e:
            raise validate.ValidationException("Error loading '%s' %s" % (url, str(e)))
        if isinstance(result, dict):
            for identifier in self.identifiers:
                if identifier not in result:
                    result[identifier] = url
                self.idx[expand_url(result[identifier], url)] = result
        else:
            self.idx[url] = result
        return result

    def validate_links(self, document):
        rvocab = set()
        for k,v in self.vocab.items():
            rvocab.add(expand_url(v, "", scoped=False, vocab=self.vocab))

        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            for d in self.checked_urls:
                if d in document:
                    if isinstance(document[d], basestring):
                        if document[d] not in self.idx and document[d] not in rvocab:
                            raise validate.ValidationException("Invalid link `%s` in field `%s`" % (document[d], d))
                    elif isinstance(document[d], list):
                        for i in document[d]:
                            if isinstance(i, basestring) and i not in self.idx and i not in rvocab:
                                raise validate.ValidationException("Invalid link `%s` in field `%s`" % (i, d))
            iterator = document.iteritems()
        else:
            return

        try:
            for key, val in iterator:
                self.validate_links(val)
        except validate.ValidationException as v:
            if isinstance(key, basestring):
                raise validate.ValidationException("At field `%s`\n%s" % (key, validate.indent(str(v))))
            else:
                raise validate.ValidationException("At position %s\n%s" % (key, validate.indent(str(v))))

        return


POINTER_DEFAULT = object()

def resolve_json_pointer(document, pointer, default=POINTER_DEFAULT):
    parts = urlparse.unquote(pointer.lstrip('/#')).split('/') \
        if pointer else []
    for part in parts:
        if isinstance(document, collections.Sequence):
            try:
                part = int(part)
            except ValueError:
                pass
        try:
            document = document[part]
        except:
            if default != POINTER_DEFAULT:
                return default
            else:
                raise ValueError('Unresolvable JSON pointer: %r' % pointer)
    return document
