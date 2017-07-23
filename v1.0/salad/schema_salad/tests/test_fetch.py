from __future__ import absolute_import
from __future__ import print_function
import unittest
import schema_salad.ref_resolver
import schema_salad.main
import schema_salad.schema
from schema_salad.jsonld_context import makerdf
import rdflib
import ruamel.yaml as yaml
import json
import os
from typing import Text
from six.moves import urllib

class TestFetcher(unittest.TestCase):
    def test_fetcher(self):
        class TestFetcher(schema_salad.ref_resolver.Fetcher):
            def __init__(self, a, b):
                pass

            def fetch_text(self, url):    # type: (Text) -> Text
                if url == "keep:abc+123/foo.txt":
                    return "hello: keepfoo"
                if url.endswith("foo.txt"):
                    return "hello: foo"
                else:
                    raise RuntimeError("Not foo.txt")

            def check_exists(self, url):  # type: (Text) -> bool
                if url.endswith("foo.txt"):
                    return True
                else:
                    return False

            def urljoin(self, base, url):
                urlsp = urllib.parse.urlsplit(url)
                if urlsp.scheme:
                    return url
                basesp = urllib.parse.urlsplit(base)

                if basesp.scheme == "keep":
                    return base + "/" + url
                return urllib.parse.urljoin(base, url)

        loader = schema_salad.ref_resolver.Loader({}, fetcher_constructor=TestFetcher)
        self.assertEqual({"hello": "foo"}, loader.resolve_ref("foo.txt")[0])
        self.assertEqual({"hello": "keepfoo"}, loader.resolve_ref("foo.txt", base_url="keep:abc+123")[0])
        self.assertTrue(loader.check_exists("foo.txt"))

        with self.assertRaises(RuntimeError):
            loader.resolve_ref("bar.txt")
        self.assertFalse(loader.check_exists("bar.txt"))

    def test_cache(self):
        loader = schema_salad.ref_resolver.Loader({})
        foo = "file://%s/foo.txt" % os.getcwd()
        loader.cache.update({foo: "hello: foo"})
        print(loader.cache)
        self.assertEqual({"hello": "foo"}, loader.resolve_ref("foo.txt")[0])
        self.assertTrue(loader.check_exists(foo))
