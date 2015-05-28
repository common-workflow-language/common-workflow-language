import os
import json
import copy
import hashlib
import logging
import collections
import requests
import urlparse
import yaml

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


class Loader(object):
    def __init__(self):
        normalize = lambda url: urlparse.urlsplit(url).geturl()
        self.fetched = NormDict(normalize)
        self.resolved = NormDict(normalize)
        self.resolving = NormDict(normalize)

    def load(self, url, base_url=None, url_fields=[]):
        base_url = base_url or 'file://%s/' % os.path.abspath('.')
        return self.resolve_ref({'id': url}, base_url, url_fields=url_fields)

    def resolve_ref(self, obj, base_url, url_fields=[]):
        ref = obj['id']
        split = urlparse.urlparse(ref)
        if split.scheme:
            url = ref
        else:
            url = urlparse.urljoin(base_url, ref)
        obj = copy.deepcopy(obj)
        obj['id'] = url
        if ref[0] == "#" or len(obj) != 1:
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
            result = self.resolve_all(fragment, doc_url, url_fields)
        finally:
            del self.resolving[url]
        result["id"] = url
        return result

    def resolve_all(self, document, base_url, url_fields):
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            if 'id' in document:
                document = self.resolve_ref(document, base_url, url_fields)
            for d in url_fields:
                if d in document and isinstance(document[d], basestring):
                    url = document[d]
                    split = urlparse.urlparse(url)
                    if not split.scheme:
                        url = urlparse.urljoin(base_url, url)
                    document[d] = url
            iterator = document.iteritems()
        else:
            return document
        for key, val in iterator:
            document[key] = self.resolve_all(val, base_url, url_fields)
        return document

    def fetch(self, url):
        if url in self.fetched:
            return self.fetched[url]
        split = urlparse.urlsplit(url)
        scheme, path = split.scheme, split.path

        if scheme in ['http', 'https'] and requests:
            resp = requests.get(url)
            try:
                resp.raise_for_status()
            except Exception as e:
                raise RuntimeError(url, e)
            result = yaml.load(resp.text)
        elif scheme == 'file':
            try:
                with open(path) as fp:
                    result = yaml.load(fp)
            except (OSError, IOError) as e:
                raise RuntimeError('Failed for %s: %s' % (url, e))
        else:
            raise ValueError('Unsupported scheme: %s' % scheme)
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

def from_url(url, base_url=None, url_fields=[]):
    return loader.load(url, base_url, url_fields=url_fields)
