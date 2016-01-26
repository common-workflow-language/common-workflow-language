import unittest
import schema_salad.ref_resolver
import schema_salad.main
import schema_salad.schema
import rdflib
import yaml

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



    # def test_domain(self):
    #     l = schema_salad.ref_resolver.Loader({})

    #     l.idx["http://example.com/stuff"] = {
    #         "$schemas": ["tests/EDAM.owl"],
    #         "$namespaces": {"edam": "http://edamontology.org/"},
    #     }

    #     ra, _ = l.resolve_all({
    #         "$import": "http://example.com/stuff",
    #         "edam:has_format": "edam:format_1915"
    #         }, "")

    #     self.assertEquals(ra, {
    #         "$schemas": ["tests/EDAM.owl"],
    #         "$namespaces": {"edam": "http://edamontology.org/"},
    #         'http://edamontology.org/has_format': 'http://edamontology.org/format_1915'
    #     })

    def test_self_validate(self):
        schema_salad.main.main(args=["schema_salad/metaschema/metaschema.yml"])
        schema_salad.main.main(args=["schema_salad/metaschema/metaschema.yml",
                                     "schema_salad/metaschema/metaschema.yml"])

    def test_jsonld_ctx(self):
        ldr, _, _ = schema_salad.schema.load_schema({
            "$base": "Y",
            "name": "X",
            "$namespaces": {
                "foo": "http://example.com/foo#"
            },
            "$graph": [{
                "name": "ExampleType",
                "type": "enum",
                "symbols": ["asym", "bsym"]}]
        })

        ra, _ = ldr.resolve_all({"foo:bar": "asym"}, "X")

        self.assertEquals(ra, {
            'http://example.com/foo#bar': 'asym'
        })

    def test_examples(self):
        self.maxDiff = None
        for a in ["field_name", "ident_res", "link_res", "vocab_res"]:
            ldr, _, _ = schema_salad.schema.load_schema("schema_salad/metaschema/%s_schema.yml" % a)
            src = ldr.resolve_all(yaml.load(open("schema_salad/metaschema/%s_src.yml" % a)), "")[0]
            proc = yaml.load(open("schema_salad/metaschema/%s_proc.yml" % a))
            self.assertEquals(proc, src)


if __name__ == '__main__':
    unittest.main()
