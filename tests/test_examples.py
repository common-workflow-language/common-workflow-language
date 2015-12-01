import unittest
import schema_salad.ref_resolver
import rdflib

class TestSchemasInContext(unittest.TestCase):
    def test_schemas(self):
        l = schema_salad.ref_resolver.Loader({
            "@schemas": ["tests/EDAM.owl"],
            "edam": "http://edamontology.org/"})

        ra, _ = l.resolve_all({
            "edam:has_format": "edam:format_1915"
            }, "")

        self.assertEquals(ra, {'http://edamontology.org/has_format': 'http://edamontology.org/format_1915'})

if __name__ == '__main__':
    unittest.main()
