from .util import get_data
import unittest
from schema_salad.main import to_one_line_messages, reformat_yaml_exception_message
from schema_salad.schema import load_schema, load_and_validate
from schema_salad.sourceline import strip_dup_lineno
from schema_salad.validate import ValidationException
from os.path import normpath
import re
import six

class TestPrintOneline(unittest.TestCase):
    def test_print_oneline(self):
        # Issue #135
        document_loader, avsc_names, schema_metadata, metaschema_loader = load_schema(
            get_data(u"tests/test_schema/CommonWorkflowLanguage.yml"))

        src = "test15.cwl"
        with self.assertRaises(ValidationException):
            try:
                load_and_validate(document_loader, avsc_names,
                                  six.text_type(get_data("tests/test_schema/"+src)), True)
            except ValidationException as e:
                msgs = to_one_line_messages(str(e)).splitlines()
                self.assertEqual(len(msgs), 2)
                m = re.match(r'^(.+:\d+:\d+:)(.+)$', msgs[0])
                self.assertTrue(msgs[0].endswith(src+":11:7: invalid field `invalid_field`, expected one of: 'loadContents', 'position', 'prefix', 'separate', 'itemSeparator', 'valueFrom', 'shellQuote'"))
                self.assertTrue(msgs[1].endswith(src+":12:7: invalid field `another_invalid_field`, expected one of: 'loadContents', 'position', 'prefix', 'separate', 'itemSeparator', 'valueFrom', 'shellQuote'"))
                print("\n", e)
                raise

    def test_print_oneline_for_invalid_yaml(self):
        # Issue #137
        document_loader, avsc_names, schema_metadata, metaschema_loader = load_schema(
            get_data(u"tests/test_schema/CommonWorkflowLanguage.yml"))

        src = "test16.cwl"
        with self.assertRaises(RuntimeError):
            try:
                load_and_validate(document_loader, avsc_names,
                                  six.text_type(get_data("tests/test_schema/"+src)), True)
            except RuntimeError as e:
                msg = reformat_yaml_exception_message(strip_dup_lineno(six.text_type(e)))
                msg = to_one_line_messages(msg)
                self.assertTrue(msg.endswith(src+":10:1: could not find expected \':\'"))
                print("\n", e)
                raise

    def test_print_oneline_for_errors_in_the_same_line(self):
        # Issue #136
        document_loader, avsc_names, schema_metadata, metaschema_loader = load_schema(
            get_data(u"tests/test_schema/CommonWorkflowLanguage.yml"))

        src = "test17.cwl"
        with self.assertRaises(ValidationException):
            try:
                load_and_validate(document_loader, avsc_names,
                                  six.text_type(get_data("tests/test_schema/"+src)), True)
            except ValidationException as e:
                msgs = to_one_line_messages(str(e)).splitlines()
                self.assertEqual(len(msgs), 2)
                self.assertTrue(msgs[0].endswith(src+":13:5: missing required field `id`"))
                self.assertTrue(msgs[1].endswith(src+":13:5: invalid field `aa`, expected one of: 'label', 'secondaryFiles', 'format', 'streamable', 'doc', 'id', 'outputBinding', 'type'"))
                print("\n", e)
                raise

    def test_print_oneline_for_errors_in_resolve_ref(self):
        # Issue #141
        document_loader, avsc_names, schema_metadata, metaschema_loader = load_schema(
            get_data(u"tests/test_schema/CommonWorkflowLanguage.yml"))

        src = "test18.cwl"
        fullpath = normpath(get_data("tests/test_schema/"+src))
        with self.assertRaises(ValidationException):
            try:
                load_and_validate(document_loader, avsc_names,
                                  six.text_type(fullpath), True)
            except ValidationException as e:
                msgs = to_one_line_messages(str(strip_dup_lineno(six.text_type(e)))).splitlines()
                # convert Windows path to Posix path
                if '\\' in fullpath:
                    fullpath = '/'+fullpath.replace('\\', '/')
                self.assertEqual(len(msgs), 1)
                self.assertTrue(msgs[0].endswith(src+':13:5: Field `type` references unknown identifier `Filea`, tried file://%s#Filea' % (fullpath)))
                print("\n", e)
                raise

    def test_for_invalid_yaml1(self):
        # Issue 143
        document_loader, avsc_names, schema_metadata, metaschema_loader = load_schema(
            get_data(u"tests/test_schema/CommonWorkflowLanguage.yml"))

        src = "test16.cwl"
        with self.assertRaises(RuntimeError):
            try:
                load_and_validate(document_loader, avsc_names,
                                  six.text_type(get_data("tests/test_schema/"+src)), True)
            except RuntimeError as e:
                msg = reformat_yaml_exception_message(strip_dup_lineno(six.text_type(e)))
                msgs = msg.splitlines()
                self.assertEqual(len(msgs), 2)
                self.assertTrue(msgs[0].endswith(src+":9:7: while scanning a simple key"))
                self.assertTrue(msgs[1].endswith(src+":10:1:   could not find expected ':'"))
                print("\n", e)
                raise

    def test_for_invalid_yaml2(self):
        # Issue 143
        document_loader, avsc_names, schema_metadata, metaschema_loader = load_schema(
            get_data(u"tests/test_schema/CommonWorkflowLanguage.yml"))

        src = "test19.cwl"
        with self.assertRaises(RuntimeError):
            try:
                load_and_validate(document_loader, avsc_names,
                                  six.text_type(get_data("tests/test_schema/"+src)), True)
            except RuntimeError as e:
                msg = reformat_yaml_exception_message(strip_dup_lineno(six.text_type(e)))
                self.assertTrue(msg.endswith(src+":1:1: expected <block end>, but found ':'"))
                print("\n", e)
                raise
