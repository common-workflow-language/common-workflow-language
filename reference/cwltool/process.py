import avro.schema
import os
import json
import validate
import copy

TOOL_CONTEXT_URL = "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json"
module_dir = os.path.dirname(os.path.abspath(__file__))

class Process(object):
    def __init__(self, toolpath_object, validateAs):
        self.names = avro.schema.Names()
        cwl_avsc = os.path.join(module_dir, 'schemas/draft-2/cwl.avsc')
        with open(cwl_avsc) as f:
            j = json.load(f)
            for t in j:
                avro.schema.make_avsc_object(t, self.names)

        self.tool = toolpath_object
        #if self.tool.get("@context") != TOOL_CONTEXT_URL:
        #    raise Exception("Missing or invalid '@context' field in tool description document, must be %s" % TOOL_CONTEXT_URL)

        # Validate tool documument
        validate.validate_ex(self.names.get_name(validateAs, ""), self.tool)

        # Import schema defs
        self.schemaDefs = {}
        if self.tool.get("schemaDefs"):
            for i in self.tool["schemaDefs"]:
                avro.schema.make_avsc_object(i, self.names)
                self.schemaDefs[i["name"]] = i

        # Build record schema from inputs
        self.inputs_record_schema = {"name": "input_record_schema", "type": "record", "fields": []}
        for i in self.tool["inputs"]:
            c = copy.copy(i)
            c["name"] = c["id"][1:]
            del c["id"]
            self.inputs_record_schema["fields"].append(c)
        avro.schema.make_avsc_object(self.inputs_record_schema, self.names)

        self.outputs_record_schema = {"name": "outputs_record_schema", "type": "record", "fields": []}
        for i in self.tool["outputs"]:
            c = copy.copy(i)
            c["name"] = c["id"][1:]
            del c["id"]
            self.outputs_record_schema["fields"].append(c)
        avro.schema.make_avsc_object(self.outputs_record_schema, self.names)
