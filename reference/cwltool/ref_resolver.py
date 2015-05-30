import os
import json
import copy
import hashlib
import logging
import collections
import requests
import urlparse
import yaml
import avro_ld.validate

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

def expand_url(url, base_url):
    split = urlparse.urlparse(url)
    if not split.scheme:
        return urlparse.urljoin(base_url, url)
    else:
        return url

class Loader(object):
    def __init__(self):
        normalize = lambda url: urlparse.urlsplit(url).geturl()
        self.fetched = NormDict(normalize)
        self.resolved = NormDict(normalize)
        self.resolving = NormDict(normalize)

    def load(self, url, base_url=None, url_fields=[], idx={}):
        base_url = base_url or 'file://%s/' % os.path.abspath('.')
        return self.resolve_ref({'import': url}, base_url, url_fields=url_fields, idx=idx)

    def resolve_ref(self, obj, base_url, url_fields=[], idx={}):
        if "import" in obj:
            if len(obj) == 1:
                ref = obj["import"]
            else:
                raise ValueError("'import' must be the only field in %s" % (str(obj)))
        elif "include" in obj:
            if len(obj) == 1:
                ref = obj["include"]
            else:
                raise ValueError("'include' must be the only field in %s" % (str(obj)))
        else:
            ref = obj['id']
        split = urlparse.urlparse(ref)
        if split.scheme:
            url = ref
        else:
            url = urlparse.urljoin(base_url, ref)

        if "include" in obj:
            return self.fetch_text(url)

        obj = copy.deepcopy(obj)
        obj['id'] = url

        if url in idx:
            raise ValueError("Object `%s` defined more than once" % (url))
        idx[url] = obj

        if ref[0] == "#" or "import" not in obj:
            return obj
        if url in self.resolved:
            return self.resolved[url]
        if url in self.resolving:
            raise RuntimeError('Circular reference for url %s' % url)
        self.resolving[url] = True
        doc_url, fragment = urlparse.urldefrag(url)
        document = self.fetch(doc_url)
        fragment = copy.deepcopy(resolve_fragment(document, fragment))
        try:
            result = self.resolve_all(fragment, doc_url, url_fields, idx=idx)
        finally:
            del self.resolving[url]
        result["id"] = url
        return result

    def resolve_all(self, document, base_url, url_fields, idx={}):
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            inc = 'include' in document
            if 'id' in document or 'import' in document or 'include' in document:
                document = self.resolve_ref(document, base_url, url_fields, idx=idx)
            if inc:
                return document
            for d in url_fields:
                if d in document:
                    if isinstance(document[d], basestring):
                        document[d] = expand_url(document[d], base_url)
                    elif isinstance(document[d], list):
                        document[d] = [expand_url(url, base_url) if isinstance(url, basestring) else url for url in document[d] ]
            iterator = document.iteritems()
        else:
            return document
        for key, val in iterator:
            document[key] = self.resolve_all(val, base_url, url_fields, idx=idx)
        return document

    def fetch_text(self, url):
        pass
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
            raise ValueError('Unsupported scheme: %s' % scheme)

    def fetch(self, url):
        if url in self.fetched:
            return self.fetched[url]
        result = yaml.load(self.fetch_text(url))
        self.fetched[url] = result
        return result

POINTER_DEFAULT = object()

def resolve_fragment(document, frag):
    if not frag:
        return document
    if isinstance(document, dict):
        if document.get("id") == frag:
            return document
        for d in document:
            r = resolve_fragment(document[d], frag)
            if r:
                return r
    elif isinstance(document, list):
        for d in document:
            r = resolve_fragment(d, frag)
            if r:
                return r
    return None

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

def from_url(url, base_url=None, url_fields=[], idx={}):
    return loader.load(url, base_url, url_fields=url_fields, idx=idx)

def validate_links(document, url_fields, idx):
    if isinstance(document, list):
        iterator = enumerate(document)
    elif isinstance(document, dict):
        for d in url_fields:
            if d in document:
                if isinstance(document[d], basestring):
                    if document[d] not in idx:
                        raise ValueError("Invalid link `%s` in field `%s`", document[d], d)
                elif isinstance(document[d], list):
                    for i in document[d]:
                        if i not in idx:
                            raise ValueError("Invalid link `%s` in field `%s`" % (i, d))
        iterator = document.iteritems()
    else:
        return idx

    try:
        for key, val in iterator:
            validate_links(val, idx, url_fields)
    except ValueError as v:
        if isinstance(key, basestring):
            raise ValueError("At field %s\n%s" % (key, avro_ld.validate.indent(str(v))))
        else:
            raise ValueError("At position %s\n%s" % (key, avro_ld.validate.indent(str(v))))

    return idx
