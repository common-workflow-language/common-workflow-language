import unittest
import schema_salad.ref_resolver
import rdflib

class TestSchemas(unittest.TestCase):
    def test_schemas(self):
        l = schema_salad.ref_resolver.Loader({})

        ra, _ = l.resolve_all({
            "$schemas": ["tests/EDAM.owl"],
            "$namespaces": {"edam": "http://edamontology.org/"},
            "edam:has_format": "edam:format_1915"
            }, "")

        self.assertEquals(ra, {
            "$schemas": ["tests/EDAM.owl"],
            "$namespaces": {"edam": "http://edamontology.org/"},
            'http://edamontology.org/has_format': 'http://edamontology.org/format_1915'
        })


    def test_import_merge(self):
        l = schema_salad.ref_resolver.Loader({})
        l.idx["http://example.com/stuff"] = {
            "a": "b"
        }

        p = l.resolve_all({"c": "d",
                           "@import": "http://example.com/stuff"}, "")

        self.assertEquals(p[0], {
            "a": "b",
            "c": "d"
        })

        p = l.resolve_all({"a": "c",
                           "@import": "http://example.com/stuff"}, "")

        self.assertEquals(p[0], {
            "a": ["c", "b"]
        })

        p = l.resolve_all({"a": ["c", "d"],
                           "@import": "http://example.com/stuff"}, "")

        self.assertEquals(p[0], {
            "a": ["c", "d", "b"]
        })


    def test_domain(self):
        l = schema_salad.ref_resolver.Loader({})

        l.idx["http://example.com/stuff"] = {
            "$schemas": ["tests/EDAM.owl"],
            "$namespaces": {"edam": "http://edamontology.org/"},
        }

        ra, _ = l.resolve_all({
            "@import": "http://example.com/stuff",
            "edam:has_format": "edam:format_1915"
            }, "")

        self.assertEquals(ra, {
            "$schemas": ["tests/EDAM.owl"],
            "$namespaces": {"edam": "http://edamontology.org/"},
            'http://edamontology.org/has_format': 'http://edamontology.org/format_1915'
        })


if __name__ == '__main__':
    unittest.main()
