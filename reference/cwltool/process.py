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
import pprint
from pkg_resources import resource_stream
import stat

_logger = logging.getLogger("cwltool")

class WorkflowException(Exception):
    pass

def get_schema():
    f = resource_stream(__name__, 'schemas/draft-2/cwl-avro.yml')
    j = yaml.load(f)
    return (j, avro_ld.schema.schema(j))

def get_feature(self, feature):
    for t in reversed(self.requirements):
        if t["class"] == feature:
            return (t, True)
    for t in reversed(self.hints):
        if t["class"] == feature:
            return (t, False)
    return (None, None)

class Process(object):
    def __init__(self, toolpath_object, validateAs, do_validate=True, **kwargs):
        (_, self.names) = get_schema()
        self.tool = toolpath_object

        if do_validate:
            try:
                # Validate tool documument
                validate.validate_ex(self.names.get_name(validateAs, ""), self.tool, strict=kwargs.get("strict"))
            except validate.ValidationException as v:
                raise validate.ValidationException("Could not validate %s as %s:\n%s" % (self.tool.get("id"), validateAs, validate.indent(str(v))))

        self.requirements = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        self.hints = kwargs.get("hints", []) + self.tool.get("hints", [])

        self.validate_hints(self.tool.get("hints", []), strict=kwargs.get("strict"))

        self.schemaDefs = {}

        sd, _ = self.get_requirement("SchemaDefRequirement")

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

            if "default" in c and "null" not in aslist(c["type"]):
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

    def validate_hints(self, hints, strict):
        for r in hints:
            try:
                if self.names.get_name(r["class"], "") is not None:
                    validate.validate_ex(self.names.get_name(r["class"], ""), r, strict=strict)
                else:
                    _logger.info(validate.ValidationException("Unknown hint %s" % (r["class"])))
            except validate.ValidationException as v:
                raise validate.ValidationException("Validating hint `%s`: %s" % (r["class"], str(v)))

    def get_requirement(self, feature):
        return get_feature(self, feature)

def empty_subtree(dirpath):
    # Test if a directory tree contains any files (does not count empty
    # subdirectories)
    for d in os.listdir(dirpath):
        d = os.path.join(dirpath, d)
        if stat.S_ISDIR(os.stat(d).st_mode):
            if empty_subtree(d) is False:
                return False
        else:
            return False
    return True
