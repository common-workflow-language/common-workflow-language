from __future__ import absolute_import
from __future__ import print_function
from .util import get_data
import unittest
from schema_salad.schema import load_schema, load_and_validate
from schema_salad.validate import ValidationException
from avro.schema import Names
import six

class TestErrors(unittest.TestCase):
    def test_errors(self):
        document_loader, avsc_names, schema_metadata, metaschema_loader = load_schema(
            get_data(u"tests/test_schema/CommonWorkflowLanguage.yml"))

        for t in ("test_schema/test1.cwl",
                  "test_schema/test2.cwl",
                  "test_schema/test3.cwl",
                  "test_schema/test4.cwl",
                  "test_schema/test5.cwl",
                  "test_schema/test6.cwl",
                  "test_schema/test7.cwl",
                  "test_schema/test8.cwl",
                  "test_schema/test9.cwl",
                  "test_schema/test10.cwl",
                  "test_schema/test11.cwl",
                  "test_schema/test12.cwl",
                  "test_schema/test13.cwl",
                  "test_schema/test14.cwl"):
            with self.assertRaises(ValidationException):
                try:
                    load_and_validate(document_loader, avsc_names,
                            six.text_type(get_data("tests/"+t)), True)
                except ValidationException as e:
                    print("\n", e)
                    raise
