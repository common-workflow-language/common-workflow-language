import os
import json
import copy
import hashlib
import logging
import collections
import requests
import urlparse
import yaml

log = logging.getLogger(__name__)


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

    def load(self, url, base_url=None):
        base_url = base_url or 'file://%s/' % os.path.abspath('.')
        return self.resolve_ref({'$ref': url}, base_url)

    def resolve_ref(self, obj, base_url):
        ref, mixin, checksum = obj.pop('$ref', None), obj.pop('$mixin', None), obj.pop('$checksum', None)
        ref = ref or mixin
        url = urlparse.urljoin(base_url, ref)
        if url in self.resolved:
            return self.resolved[url]
        if url in self.resolving:
            raise RuntimeError('Circular reference for url %s' % url)
        self.resolving[url] = True
        doc_url, pointer = urlparse.urldefrag(url)
        document = self.fetch(doc_url)
        fragment = copy.deepcopy(resolve_pointer(document, pointer))
        try:
            self.verify_checksum(checksum, fragment)
            if isinstance(fragment, dict) and mixin:
                fragment = dict(obj, **fragment)
            result = self.resolve_all(fragment, doc_url)
        finally:
            del self.resolving[url]
        return result

    def resolve_all(self, document, base_url):
        if isinstance(document, list):
            iterator = enumerate(document)
        elif isinstance(document, dict):
            if '$ref' in document or '$mixin' in document:
                return self.resolve_ref(document, base_url)
            iterator = document.iteritems()
        else:
            return document
        for key, val in iterator:
            document[key] = self.resolve_all(val, base_url)
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

    def verify_checksum(self, checksum, document):
        if not checksum:
            return
        hash_method, hexdigest = checksum.split('$')
        if hexdigest != self.checksum(document, hash_method):
            raise RuntimeError('Checksum does not match: %s' % checksum)

    def checksum(self, document, method='sha1'):
        if method not in ('md5', 'sha1'):
            raise NotImplementedError('Unsupported hash method: %s' % method)
        normalized = json.dumps(document, sort_keys=True, separators=(',', ':'))
        return getattr(hashlib, method)(normalized).hexdigest


POINTER_DEFAULT = object()


def resolve_pointer(document, pointer, default=POINTER_DEFAULT):
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


def to_json(obj, fp=None):
    default = lambda o: (o.__json__() if callable(getattr(o, '__json__', None))
                         else str(o))
    kwargs = dict(default=default, indent=2, sort_keys=True)
    return json.dump(obj, fp, **kwargs) if fp else json.dumps(obj, **kwargs)


def from_url(url, base_url=None):
    return loader.load(url, base_url)
