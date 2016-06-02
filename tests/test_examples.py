import unittest
import schema_salad.ref_resolver
import schema_salad.main
import schema_salad.schema
import rdflib
import ruamel.yaml as yaml
try:
    from ruamel.yaml import CSafeLoader as SafeLoader
except ImportError:
    from ruamel.yaml import SafeLoader


class TestSchemas(unittest.TestCase):
    def test_schemas(self):
        l = schema_salad.ref_resolver.Loader({})

        ra, _ = l.resolve_all({
            "$schemas": ["tests/EDAM.owl"],
            "$namespaces": {"edam": "http://edamontology.org/"},
            "edam:has_format": "edam:format_1915"
        }, "")

        self.assertEqual(ra, {
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
        schema_salad.main.main(argsl=["schema_salad/metaschema/metaschema.yml"])
        schema_salad.main.main(argsl=["schema_salad/metaschema/metaschema.yml",
                                     "schema_salad/metaschema/metaschema.yml"])

    def test_jsonld_ctx(self):
        ldr, _, _, _ = schema_salad.schema.load_schema({
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

        self.assertEqual(ra, {
            'http://example.com/foo#bar': 'asym'
        })

    maxDiff = None

    def test_idmap(self):
        ldr = schema_salad.ref_resolver.Loader({})
        ldr.add_context({
            "inputs": {
                "@id": "http://example.com/inputs",
                "mapSubject": "id",
                "mapPredicate": "a"
            },
            "outputs": {
                "@type": "@id",
                "identity": True,
            },
            "id": "@id"})

        ra, _ = ldr.resolve_all({
            "id": "stuff",
            "inputs": {
                "zip": 1,
                "zing": 2
            },
            "outputs": ["out"],
            "other": {
                'n': 9
            }
        }, "http://example2.com/")

        self.assertEqual("http://example2.com/#stuff", ra["id"])
        for item in ra["inputs"]:
            if item["a"] == 2:
                self.assertEquals('http://example2.com/#stuff/zing', item["id"])
            else:
                self.assertEquals('http://example2.com/#stuff/zip', item["id"])
        self.assertEquals(['http://example2.com/#stuff/out'], ra['outputs'])
        self.assertEquals({'n': 9}, ra['other'])

    def test_scoped_ref(self):
        ldr = schema_salad.ref_resolver.Loader({})
        ldr.add_context({
            "scatter": {
                "@type": "@id",
                "scopedRef": True,
            },
            "source": {
                "@type": "@id",
                "scopedRef": True,
            },
            "in": {
                "mapSubject": "id",
                "mapPredicate": "source"
            },
            "inputs": {
                "mapSubject": "id",
                "mapPredicate": "type"
            },
            "steps": {
                "mapSubject": "id"
            },
            "id": "@id"})

        ra, _ = ldr.resolve_all({
            "inputs": {
                "inp": "string"
            },
            "steps": {
                "step1": {
                    "in": {
                        "echo_in": "inp"
                    },
                    "scatter": "echo_in"
                }
            }
        }, "http://example2.com/")

        self.assertEquals({'inputs': [{
                'id': 'http://example2.com/#inp',
                'type': 'string'
            }],
            'steps': [{
                    'id': 'http://example2.com/#step1',
                    'scatter': 'http://example2.com/#step1/echo_in',
                    'in': [{
                            'id': 'http://example2.com/#step1/echo_in',
                            'source': 'http://example2.com/#inp'
                    }]
                }]
        }, ra)


    def test_examples(self):
        self.maxDiff = None
        for a in ["field_name", "ident_res", "link_res", "vocab_res"]:
            ldr, _, _, _ = schema_salad.schema.load_schema(
                "schema_salad/metaschema/%s_schema.yml" % a)
            with open("schema_salad/metaschema/%s_src.yml" % a) as src_fp:
                src = ldr.resolve_all(
                    yaml.load(src_fp, Loader=SafeLoader), "", checklinks=False)[0]
            with open("schema_salad/metaschema/%s_proc.yml" % a) as src_proc:
                proc = yaml.load(src_proc, Loader=SafeLoader)
            self.assertEqual(proc, src)

    def test_yaml_float_test(self):
        self.assertEqual(yaml.load("float-test: 2e-10")["float-test"], 2e-10)

if __name__ == '__main__':
    unittest.main()
