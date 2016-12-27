import unittest
import schema_salad.ref_resolver
import schema_salad.main
import schema_salad.schema
from schema_salad.jsonld_context import makerdf
from pkg_resources import Requirement, resource_filename, ResolutionError  # type: ignore
import rdflib
import ruamel.yaml
import json
import os
from schema_salad.sourceline import cmap

try:
    from ruamel.yaml import CSafeLoader as SafeLoader
except ImportError:
    from ruamel.yaml import SafeLoader  # type: ignore

from ruamel.yaml.comments import CommentedSeq, CommentedMap

def get_data(filename):
    filepath = None
    try:
        filepath = resource_filename(
            Requirement.parse("schema-salad"), filename)
    except ResolutionError:
        pass
    if not filepath or not os.path.isfile(filepath):
        filepath = os.path.join(os.path.dirname(__file__), os.pardir, filename)
    return filepath


class TestSchemas(unittest.TestCase):
    def test_schemas(self):
        l = schema_salad.ref_resolver.Loader({})

        ra, _ = l.resolve_all(cmap({
            u"$schemas": ["file://" + get_data("tests/EDAM.owl")],
            u"$namespaces": {u"edam": u"http://edamontology.org/"},
            u"edam:has_format": u"edam:format_1915"
        }), "")

        self.assertEqual({
            u"$schemas": ["file://" + get_data("tests/EDAM.owl")],
            u"$namespaces": {u"edam": u"http://edamontology.org/"},
            u'http://edamontology.org/has_format': u'http://edamontology.org/format_1915'
        }, ra)

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
        self.assertEqual(0, schema_salad.main.main(
            argsl=[get_data("metaschema/metaschema.yml")]))
        self.assertEqual(0, schema_salad.main.main(
            argsl=[get_data("metaschema/metaschema.yml"),
                   get_data("metaschema/metaschema.yml")]))

    def test_avro_regression(self):
        self.assertEqual(0, schema_salad.main.main(
            argsl=[get_data("tests/Process.yml")]))

    def test_jsonld_ctx(self):
        ldr, _, _, _ = schema_salad.schema.load_schema(cmap({
            "$base": "Y",
            "name": "X",
            "$namespaces": {
                "foo": "http://example.com/foo#"
            },
            "$graph": [{
                "name": "ExampleType",
                "type": "enum",
                "symbols": ["asym", "bsym"]}]
        }))

        ra, _ = ldr.resolve_all(cmap({"foo:bar": "asym"}), "X")

        self.assertEqual(ra, {
            'http://example.com/foo#bar': 'asym'
        })

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

        ra, _ = ldr.resolve_all(cmap({
            "id": "stuff",
            "inputs": {
                "zip": 1,
                "zing": 2
            },
            "outputs": ["out"],
            "other": {
                'n': 9
            }
        }), "http://example2.com/")

        self.assertEqual("http://example2.com/#stuff", ra["id"])
        for item in ra["inputs"]:
            if item["a"] == 2:
                self.assertEquals(
                    'http://example2.com/#stuff/zing', item["id"])
            else:
                self.assertEquals('http://example2.com/#stuff/zip', item["id"])
        self.assertEquals(['http://example2.com/#stuff/out'], ra['outputs'])
        self.assertEquals({'n': 9}, ra['other'])

    def test_scoped_ref(self):
        ldr = schema_salad.ref_resolver.Loader({})
        ldr.add_context({
            "scatter": {
                "@type": "@id",
                "refScope": 0,
            },
            "source": {
                "@type": "@id",
                "refScope": 2,
            },
            "in": {
                "mapSubject": "id",
                "mapPredicate": "source"
            },
            "out": {
                "@type": "@id",
                "identity": True
            },
            "inputs": {
                "mapSubject": "id",
                "mapPredicate": "type"
            },
            "outputs": {
                "mapSubject": "id",
            },
            "steps": {
                "mapSubject": "id"
            },
            "id": "@id"})

        ra, _ = ldr.resolve_all(cmap({
            "inputs": {
                "inp": "string",
                "inp2": "string"
            },
            "outputs": {
                "out": {
                    "type": "string",
                    "source": "step2/out"
                }
            },
            "steps": {
                "step1": {
                    "in": {
                        "inp": "inp",
                        "inp2": "#inp2",
                        "inp3": ["inp", "inp2"]
                    },
                    "out": ["out"],
                    "scatter": "inp"
                },
                "step2": {
                    "in": {
                        "inp": "step1/out"
                    },
                    "scatter": "inp",
                    "out": ["out"]
                }
            }
        }), "http://example2.com/")

        self.assertEquals(
            {'inputs': [{
                'id': 'http://example2.com/#inp',
                'type': 'string'
            }, {
                'id': 'http://example2.com/#inp2',
                'type': 'string'
            }],
                'outputs': [{
                    'id': 'http://example2.com/#out',
                    'type': 'string',
                    'source': 'http://example2.com/#step2/out'
                }],
                'steps': [{
                    'id': 'http://example2.com/#step1',
                    'scatter': 'http://example2.com/#step1/inp',
                    'in': [{
                        'id': 'http://example2.com/#step1/inp',
                        'source': 'http://example2.com/#inp'
                    }, {
                        'id': 'http://example2.com/#step1/inp2',
                        'source': 'http://example2.com/#inp2'
                    }, {
                        'id': 'http://example2.com/#step1/inp3',
                        'source': ['http://example2.com/#inp', 'http://example2.com/#inp2']
                    }],
                    "out": ["http://example2.com/#step1/out"],
                }, {
                    'id': 'http://example2.com/#step2',
                    'scatter': 'http://example2.com/#step2/inp',
                    'in': [{
                        'id': 'http://example2.com/#step2/inp',
                        'source': 'http://example2.com/#step1/out'
                    }],
                    "out": ["http://example2.com/#step2/out"],
                }]
            }, ra)

    def test_examples(self):
        for a in ["field_name", "ident_res", "link_res", "vocab_res"]:
            ldr, _, _, _ = schema_salad.schema.load_schema(
                get_data("metaschema/%s_schema.yml" % a))
            with open(get_data("metaschema/%s_src.yml" % a)) as src_fp:
                src = ldr.resolve_all(
                    ruamel.yaml.round_trip_load(src_fp), "",
                    checklinks=False)[0]
            with open(get_data("metaschema/%s_proc.yml" % a)) as src_proc:
                proc = ruamel.yaml.safe_load(src_proc)
            self.assertEqual(proc, src)

    def test_yaml_float_test(self):
        self.assertEqual(ruamel.yaml.safe_load("float-test: 2e-10")["float-test"],
                2e-10)

    def test_typedsl_ref(self):
        ldr = schema_salad.ref_resolver.Loader({})
        ldr.add_context({
            "File": "http://example.com/File",
            "null": "http://example.com/null",
            "array": "http://example.com/array",
            "type": {
                "@type": "@vocab",
                "typeDSL": True
            }
        })

        ra, _ = ldr.resolve_all(cmap({"type": "File"}), "")
        self.assertEqual({'type': 'File'}, ra)

        ra, _ = ldr.resolve_all(cmap({"type": "File?"}), "")
        self.assertEqual({'type': ['null', 'File']}, ra)

        ra, _ = ldr.resolve_all(cmap({"type": "File[]"}), "")
        self.assertEqual({'type': {'items': 'File', 'type': 'array'}}, ra)

        ra, _ = ldr.resolve_all(cmap({"type": "File[]?"}), "")
        self.assertEqual(
            {'type': ['null', {'items': 'File', 'type': 'array'}]}, ra)

    def test_scoped_id(self):
        ldr = schema_salad.ref_resolver.Loader({})
        ctx = {
            "id": "@id",
            "location": {
                "@id": "@id",
                "@type": "@id"
            },
            "bar": "http://example.com/bar",
            "ex": "http://example.com/"
        }
        ldr.add_context(ctx)

        ra, _ = ldr.resolve_all(cmap({
            "id": "foo",
            "bar": {
                "id": "baz"
            }
        }), "http://example.com")
        self.assertEqual({'id': 'http://example.com/#foo',
                          'bar': {
                              'id': 'http://example.com/#foo/baz'},
                          }, ra)

        g = makerdf(None, ra, ctx)
        print(g.serialize(format="n3"))

        ra, _ = ldr.resolve_all(cmap({
            "location": "foo",
            "bar": {
                "location": "baz"
            }
        }), "http://example.com", checklinks=False)
        self.assertEqual({'location': 'http://example.com/foo',
                          'bar': {
                              'location': 'http://example.com/baz'},
                          }, ra)

        g = makerdf(None, ra, ctx)
        print(g.serialize(format="n3"))

        ra, _ = ldr.resolve_all(cmap({
            "id": "foo",
            "bar": {
                "location": "baz"
            }
        }), "http://example.com", checklinks=False)
        self.assertEqual({'id': 'http://example.com/#foo',
                          'bar': {
                              'location': 'http://example.com/baz'},
                          }, ra)

        g = makerdf(None, ra, ctx)
        print(g.serialize(format="n3"))

        ra, _ = ldr.resolve_all(cmap({
            "location": "foo",
            "bar": {
                "id": "baz"
            }
        }), "http://example.com", checklinks=False)
        self.assertEqual({'location': 'http://example.com/foo',
                          'bar': {
                              'id': 'http://example.com/#baz'},
                          }, ra)

        g = makerdf(None, ra, ctx)
        print(g.serialize(format="n3"))

    def test_mixin(self):
        base_url = "file://" + os.getcwd() + "/tests/"
        ldr = schema_salad.ref_resolver.Loader({})
        ra = ldr.resolve_ref(cmap({"$mixin": get_data("tests/mixin.yml"), "one": "five"}),
                             base_url=base_url)
        self.assertEqual({'id': 'four', 'one': 'five'}, ra[0])
        ldr = schema_salad.ref_resolver.Loader({"id": "@id"})

        ra = ldr.resolve_all(cmap([{
            "id": "a",
            "m": {"$mixin": get_data("tests/mixin.yml")}
        }, {
            "id": "b",
            "m": {"$mixin": get_data("tests/mixin.yml")}
        }]), base_url=base_url)
        self.assertEqual([{
            'id': base_url + '#a',
            'm': {
                'id': base_url + u'#a/four',
                'one': 'two'
            },
        }, {
            'id': base_url + '#b',
            'm': {
                'id': base_url + u'#b/four',
                'one': 'two'}
        }], ra[0])

    def test_fragment(self):
        ldr = schema_salad.ref_resolver.Loader({"id": "@id"})
        b, _ = ldr.resolve_ref("schema_salad/tests/frag.yml#foo2")
        self.assertEquals({"id": b["id"], "bar":"b2"}, b)


if __name__ == '__main__':
    unittest.main()
