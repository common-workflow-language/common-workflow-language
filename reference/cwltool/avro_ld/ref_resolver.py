import os
import json
import hashlib
import logging
import collections
import requests
import urlparse
import yaml
import validate

log = logging.getLogger("cwltool")

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

def expand_url(url, base_url):
    split = urlparse.urlparse(url)
    if split.scheme:
        return url
    else:
        return urlparse.urljoin(base_url, url)

class Loader(object):
    def __init__(self):
        normalize = lambda url: urlparse.urlsplit(url).geturl()
        self.idx = NormDict(normalize)
        self.url_fields = []

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
                if "id" in obj:
                    ref = obj["id"]
                else:
                    raise ValueError("Object `%s` does not have `id` field" % obj)

        if not isinstance(ref, basestring):
            raise ValueError("Must be string: `%s`" % str(ref))

        url = expand_url(ref, base_url)

        # Has this reference been loaded already?
        if url in self.idx:
            return self.idx[url]

        # "include" directive means load raw text
        if obj and "include" in obj:
            return self.fetch_text(url)

        if obj:
            obj["id"] = url
            self.idx[url] = obj
        else:
            # Load structured document
            doc_url, frg = urlparse.urldefrag(url)
            if doc_url in self.idx:
                raise validate.ValidationException("Reference `#%s` not found in file `%s`." % (frg, doc_url))
            obj = self.fetch(doc_url)

        # Recursively expand urls and resolve directives
        self.resolve_all(obj, url)

        # Requested reference should be in the index now, otherwise it's a bad reference
        if self.idx.get(url) is not None:
            return self.idx[url]
        else:
            raise RuntimeError("Reference `%s` is not in the index.  Index contains:\n  %s" % (url, "\n  ".join(self.idx)))

    def resolve_all(self, document, base_url):
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            inc = 'include' in document
            if 'id' in document or 'import' in document or 'include' in document:
                document = self.resolve_ref(document, base_url)
            if inc:
                return document

            for d in self.url_fields:
                if d in document:
                    if isinstance(document[d], basestring):
                        document[d] = expand_url(document[d], base_url)
                    elif isinstance(document[d], list):
                        document[d] = [expand_url(url, base_url) if isinstance(url, basestring) else url for url in document[d] ]
            iterator = document.iteritems()
        else:
            return document

        for key, val in iterator:
            try:
                document[key] = self.resolve_all(val, base_url)
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
                    return fp.read()
            except (OSError, IOError) as e:
                raise RuntimeError('Failed for %s: %s' % (url, e))
        else:
            raise ValueError('Unsupported scheme in url: %s' % url)

    def fetch(self, url):
        if url in self.idx:
            return self.idx[url]
        result = yaml.load(self.fetch_text(url))
        if isinstance(result, dict):
            if "id" not in result:
                result["id"] = url
            self.idx[expand_url(result["id"], url)] = result
        else:
            self.idx[url] = result
        return result

    def validate_links(self, document):
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            for d in self.url_fields:
                if d in document:
                    if isinstance(document[d], basestring):
                        if document[d] not in self.idx:
                            raise validate.ValidationException("Invalid link `%s` in field `%s`" % (document[d], d))
                    elif isinstance(document[d], list):
                        for i in document[d]:
                            if isinstance(i, basestring) and i not in self.idx:
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

loader = Loader()
