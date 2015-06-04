import avro.schema
import os
import json
import avro_ld.validate as validate
import copy
import yaml
import copy
import logging
import pprint
from aslist import aslist
import avro_ld.schema
import urlparse

module_dir = os.path.dirname(os.path.abspath(__file__))

_logger = logging.getLogger("cwltool")

class WorkflowException(Exception):
    pass

def get_schema():
    cwl_avsc = os.path.join(module_dir, 'schemas/draft-2/cwl-avro.yml')
    with open(cwl_avsc) as f:
        j = yaml.load(f)
        return (j, avro_ld.schema.schema(j))

def get_feature(feature, **kwargs):
    if kwargs.get("requirements"):
        for t in reversed(kwargs["requirements"]):
            if t["class"] == feature:
                return (t, True)
    if kwargs.get("hints"):
        for t in reversed(kwargs.get("hints", [])):
            if t["class"] == feature:
                return (t, False)
    return (None, None)

class Process(object):
    def __init__(self, toolpath_object, validateAs, docpath, **kwargs):
        (_, self.names) = get_schema()
        self.docpath = docpath

        self.tool = toolpath_object

        try:
            # Validate tool documument
            validate.validate_ex(self.names.get_name(validateAs, ""), self.tool, **kwargs)
        except validate.ValidationException as v:
            raise validate.ValidationException("Could not validate %s:\n%s" % (self.tool.get("id"), validate.indent(str(v))))

        self.validate_requirements(self.tool, "requirements")
        self.validate_requirements(self.tool, "hints")

        for t in self.tool.get("requirements", []):
            t["_docpath"] = docpath

        for t in self.tool.get("hints", []):
            t["_docpath"] = docpath

        avro.schema.make_avsc_object({
            "name": "Any",
            "type": "enum",
            "symbols": ["Any"]
        }, self.names)

        self.schemaDefs = {}

        sd, _ = get_feature("SchemaDefRequirement", requirements=self.tool.get("requirements"), hints=self.tool.get("hints"))
        if sd:
            for i in sd["types"]:
                avro.schema.make_avsc_object(i, self.names)
                self.schemaDefs[i["name"]] = i

        # Build record schema from inputs
        self.inputs_record_schema = {"name": "input_record_schema", "type": "record", "fields": []}
        for i in self.tool["inputs"]:
            c = copy.copy(i)
            doc_url, fragment = urlparse.urldefrag(c['id'])
            c["name"] = fragment
            del c["id"]

            if "type" not in c:
                raise validate.ValidationException("Missing `type` in parameter `%s`" % c["name"])

            if "default" in c:
                c["type"] = ["null"] + aslist(c["type"])
            else:
                c["type"] = c["type"]
            self.inputs_record_schema["fields"].append(c)

        avro.schema.make_avsc_object(self.inputs_record_schema, self.names)

        self.outputs_record_schema = {"name": "outputs_record_schema", "type": "record", "fields": []}
        for i in self.tool["outputs"]:
            c = copy.copy(i)
            doc_url, fragment = urlparse.urldefrag(c['id'])
            c["name"] = fragment
            del c["id"]

            if "type" not in c:
                raise validate.ValidationException("Missing `type` in parameter `%s`" % c["name"])

            if "default" in c:
                c["type"] = ["null"] + aslist(c["type"])
            else:
                c["type"] = c["type"]
            self.outputs_record_schema["fields"].append(c)

        avro.schema.make_avsc_object(self.outputs_record_schema, self.names)

    def validate_requirements(self, tool, field):
        for r in tool.get(field, []):
            try:
                if self.names.get_name(r["class"], "") is None:
                    raise validate.ValidationException("Unknown requirement %s" % (r["class"]))
                validate.validate_ex(self.names.get_name(r["class"], ""), r)
                if "requirements" in r:
                    self.validate_requirements(r, "requirements")
                if "hints" in r:
                    self.validate_requirements(r, "hints")
            except validate.ValidationException as v:
                err = "While validating %s %s\n%s" % (field, r["class"], validate.indent(str(v)))
                if field == "hints":
                    _logger.warn(err)
                else:
                    raise validate.ValidationException(err)
