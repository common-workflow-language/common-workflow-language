import os
import json
import hashlib
import logging
import collections
import requests
import urlparse
import yaml
import validate
import pprint
from aslist import aslist

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

class Loader(object):
    def __init__(self, ctx):
        normalize = lambda url: urlparse.urlsplit(url).geturl()
        self.idx = NormDict(normalize)
        self.ctx = {}
        self.add_context(ctx)

    def expand_url(self, url, base_url, scoped=False, vocab_term=False):
        if url in ("@id", "@type"):
            return url

        if vocab_term and url in self.vocab:
            return url

        if self.vocab and ":" in url:
            prefix = url.split(":")[0]
            if prefix in self.vocab:
                url = self.vocab[prefix] + url[len(prefix)+1:]

        split = urlparse.urlsplit(url)

        if split.scheme:
            pass
        elif scoped and not split.fragment:
            splitbase = urlparse.urlsplit(base_url)
            frg = ""
            if splitbase.fragment:
                frg = splitbase.fragment + "/" + split.path
            else:
                frg = split.path
            url = urlparse.urlunsplit((splitbase.scheme, splitbase.netloc, splitbase.path, splitbase.query, frg))
        else:
            url = urlparse.urljoin(base_url, url)

        if vocab_term and url in self.rvocab:
            return self.rvocab[url]
        else:
            return url


    def add_context(self, newcontext):
        self.url_fields = []
        self.vocab_fields = []
        self.identifiers = []
        self.identity_links = []
        self.standalone = []
        self.nolinkcheck = []
        self.vocab = {}
        self.rvocab = {}

        self.ctx.update(newcontext)

        _logger.debug("ctx is %s", self.ctx)

        for c in self.ctx:
            if self.ctx[c] == "@id":
                self.identifiers.append(c)
                self.identity_links.append(c)
            elif isinstance(self.ctx[c], dict) and self.ctx[c].get("@type") == "@id":
                self.url_fields.append(c)
                if self.ctx[c].get("identity", False):
                    self.identity_links.append(c)
            elif isinstance(self.ctx[c], dict) and self.ctx[c].get("@type") == "@vocab":
                self.url_fields.append(c)
                self.vocab_fields.append(c)

            if isinstance(self.ctx[c], dict) and self.ctx[c].get("noLinkCheck"):
                self.nolinkcheck.append(c)

            if isinstance(self.ctx[c], dict) and "@id" in self.ctx[c]:
                self.vocab[c] = self.ctx[c]["@id"]
            elif isinstance(self.ctx[c], basestring):
                self.vocab[c] = self.ctx[c]

        for k,v in self.vocab.items():
            self.rvocab[self.expand_url(v, "", scoped=False)] = k

        _logger.debug("identifiers is %s", self.identifiers)
        _logger.debug("identity_links is %s", self.identity_links)
        _logger.debug("url_fields is %s", self.url_fields)
        _logger.debug("vocab_fields is %s", self.vocab_fields)
        _logger.debug("vocab is %s", self.vocab)


    def resolve_ref(self, ref, base_url=None):
        base_url = base_url or 'file://%s/' % os.path.abspath('.')

        obj = None
        inc = False

        # If `ref` is a dict, look for special directives.
        if isinstance(ref, dict):
            obj = ref
            if "@import" in ref:
                ref = obj["@import"]
                obj = None
            elif "@include" in obj:
                if len(obj) == 1:
                    ref = obj["@include"]
                    inc = True
                    obj = None
                else:
                    raise ValueError("'@include' must be the only field in %s" % (str(obj)))
            else:
                ref = None
                for identifier in self.identifiers:
                    if identifier in obj:
                        ref = obj[identifier]
                        break
                if not ref:
                    raise ValueError("Object `%s` does not have identifier field in %s" % (obj, self.identifiers))

        if not isinstance(ref, basestring):
            raise ValueError("Must be string: `%s`" % str(ref))

        url = self.expand_url(ref, base_url, scoped=(obj is not None))

        # Has this reference been loaded already?
        if url in self.idx:
            return self.idx[url], {}

        # "@include" directive means load raw text
        if inc:
            return self.fetch_text(url), {}

        if obj:
            for identifier in self.identifiers:
                obj[identifier] = url
        else:
            # Load structured document
            doc_url, frg = urlparse.urldefrag(url)
            if doc_url in self.idx:
                raise validate.ValidationException("Reference `#%s` not found in file `%s`." % (frg, doc_url))
            obj = self.fetch(doc_url)

        # Recursively expand urls and resolve directives
        obj, metadata = self.resolve_all(obj, url)

        # Requested reference should be in the index now, otherwise it's a bad reference
        if url in self.idx:
            obj = self.idx[url]
            if "@graph" in obj:
                metadata = {k: v for k,v in obj.items() if k != "@graph"}
                obj = obj["@graph"]
                return obj, metadata
            else:
                return obj, metadata
        else:
            raise RuntimeError("Reference `%s` is not in the index.  Index contains:\n  %s" % (url, "\n  ".join(self.idx)))

    def resolve_all(self, document, base_url):
        loader = self
        metadata = {}

        if isinstance(document, dict):
            inc = '@include' in document
            if  '@import' in document or '@include' in document:
                document, _ = self.resolve_ref(document, base_url)
            else:
                for identifer in self.identity_links:
                    if identifer in document:
                        if isinstance(document[identifer], basestring):
                            document[identifer] = self.expand_url(document[identifer], base_url, scoped=True)
                            if document[identifer] not in self.idx or isinstance(self.idx[document[identifer]], basestring):
                                self.idx[document[identifer]] = document
                            base_url = document[identifer]
                        elif isinstance(document[identifer], list):
                            for n, v in enumerate(document[identifer]):
                                document[identifer][n] = self.expand_url(document[identifer][n], base_url, scoped=True)
                                if document[identifer][n] not in self.idx:
                                    self.idx[document[identifer][n]] = document[identifer][n]
            if inc:
                return document, {}

            if isinstance(document, dict) and "@context" in document:
                loader = Loader(self.ctx)
                loader.idx = self.idx
                loader.add_context(document["@context"])
                if "@base" in loader.ctx:
                    base_url = loader.ctx["@base"]

            if "@graph" in document:
                metadata = {k: v for k,v in document.items() if k != "@graph"}
                document = document["@graph"]
                metadata, _ = self.resolve_all(metadata, base_url)

        elif isinstance(document, list):
            pass
        else:
            return document, metadata

        try:
            if isinstance(document, dict):
                for d in document:
                    d2 = self.expand_url(d, "", scoped=False, vocab_term=True)
                    if d != d2:
                        document[d2] = document[d]
                        del document[d]

                for d in loader.url_fields:
                    if d in document:
                        if isinstance(document[d], basestring):
                            document[d] = loader.expand_url(document[d], base_url, scoped=False, vocab_term=(d in loader.vocab_fields))
                        elif isinstance(document[d], list):
                            document[d] = [loader.expand_url(url, base_url, scoped=False, vocab_term=(d in loader.vocab_fields)) if isinstance(url, basestring) else url for url in document[d] ]

                for key, val in document.items():
                    document[key], _ = loader.resolve_all(val, base_url)

            elif isinstance(document, list):
                i = 0
                while i < len(document):
                    val = document[i]
                    if isinstance(val, dict) and "@import" in val and val.get("inline"):
                        l, _ = loader.resolve_all(val, base_url)
                        del document[i]
                        for item in aslist(l):
                            document.insert(i, item)
                            i += 1
                    else:
                        document[i], _ = loader.resolve_all(val, base_url)
                        i += 1

        except validate.ValidationException as v:
            if isinstance(key, basestring):
                raise validate.ValidationException("Validation error in field %s:\n%s" % (key, validate.indent(str(v))))
            else:
                raise validate.ValidationException("Validation error in position %i:\n%s" % (key, validate.indent(str(v))))

        return document, metadata

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
        if isinstance(result, dict) and self.identifiers:
            for identifier in self.identifiers:
                if identifier not in result:
                    result[identifier] = url
                self.idx[self.expand_url(result[identifier], url)] = result
        else:
            self.idx[url] = result
        return result

    def check_file(self, fn):
        if fn.startswith("file://"):
            return os.path.exists(fn[7:])
        else:
            return False

    def validate_link(self, field, link):
        if field in self.nolinkcheck:
            return True
        if isinstance(link, basestring):
            if field in self.vocab_fields:
                if link not in self.vocab and link not in self.idx and link not in self.rvocab:
                    if not self.check_file(link):
                        raise validate.ValidationException("Field `%s` contains undefined reference to `%s`" % (field, link))
            elif link not in self.idx and link not in self.rvocab:
                if not self.check_file(link):
                    raise validate.ValidationException("Field `%s` contains undefined reference to `%s`" % (field, link))
        elif isinstance(link, list):
            errors = []
            for i in link:
                try:
                    self.validate_link(field, i)
                except validate.ValidationException as v:
                    errors.append(v)
            if errors:
                raise validate.ValidationException("\n".join([str(e) for e in errors]))
        elif isinstance(link, dict):
            self.validate_links(link)
        return True

    def getid(self, d):
        if isinstance(d, dict):
            for i in self.identifiers:
                if i in d:
                    if isinstance(d[i], basestring):
                        return d[i]
        return None

    def validate_links(self, document):
        docid = self.getid(document)
        if docid is None:
            docid = ""

        errors = []
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            try:
                for d in self.url_fields:
                    if d not in self.identity_links and d in document:
                        self.validate_link(d, document[d])
            except validate.ValidationException as v:
                errors.append(v)
            iterator = document.iteritems()
        else:
            return

        for key, val in iterator:
            try:
                self.validate_links(val)
            except validate.ValidationException as v:
                if key not in self.nolinkcheck:
                    docid = self.getid(val)
                    if docid:
                        errors.append(validate.ValidationException("While checking object `%s`\n%s" % (docid, validate.indent(str(v)))))
                    else:
                        if isinstance(key, basestring):
                            errors.append(validate.ValidationException("While checking field `%s`\n%s" % (key, validate.indent(str(v)))))
                        else:
                            errors.append(validate.ValidationException("While checking position %s\n%s" % (key, validate.indent(str(v)))))

        if errors:
            if len(errors) > 1:
                raise validate.ValidationException("\n".join([str(e) for e in errors]))
            else:
                raise errors[0]
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
