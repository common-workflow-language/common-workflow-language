import avro.schema
import os
import json
import schema_salad.validate as validate
import copy
import yaml
import copy
import logging
import pprint
from aslist import aslist
import schema_salad.schema
import urlparse
import pprint
from pkg_resources import resource_stream
import stat
from builder import Builder
import tempfile
import glob
from errors import WorkflowException
from pathmapper import abspath

_logger = logging.getLogger("cwltool")

supportedProcessRequirements = ["DockerRequirement",
                                "ExpressionEngineRequirement",
                                "SchemaDefRequirement",
                                "EnvVarRequirement",
                                "CreateFileRequirement",
                                "ScatterFeatureRequirement",
                                "SubworkflowFeatureRequirement",
                                "MultipleInputFeatureRequirement"]

def get_schema():
    f = resource_stream(__name__, 'schemas/draft-3/cwl-avro.yml')
    j = yaml.load(f)
    j["name"] = "https://w3id.org/cwl/cwl"
    return schema_salad.schema.load_schema(j)

def get_feature(self, feature):
    for t in reversed(self.requirements):
        if t["class"] == feature:
            return (t, True)
    for t in reversed(self.hints):
        if t["class"] == feature:
            return (t, False)
    return (None, None)

def shortname(inputid):
    (_, d) = urlparse.urldefrag(inputid)
    return d.split("/")[-1].split(".")[-1]

class StdFsAccess(object):
    def __init__(self, basedir):
        self.basedir = basedir

    def _abs(self, p):
        return abspath(p, self.basedir)

    def glob(self, pattern):
        return glob.glob(self._abs(pattern))

    def open(self, fn, mode):
        return open(self._abs(fn), mode)

    def exists(self, fn):
        return os.path.exists(self._abs(fn))

class Process(object):
    def __init__(self, toolpath_object, validateAs, do_validate=True, **kwargs):
        (_, self.names, _) = get_schema()
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
            sdtypes = sd["types"]
            av = schema_salad.schema.make_valid_avro(sdtypes, {t["name"]: t for t in sdtypes}, set())
            for i in av:
                self.schemaDefs[i["name"]] = i
            avro.schema.make_avsc_object(av, self.names)

        # Build record schema from inputs
        self.inputs_record_schema = {"name": "input_record_schema", "type": "record", "fields": []}
        self.outputs_record_schema = {"name": "outputs_record_schema", "type": "record", "fields": []}

        for key in ("inputs", "outputs"):
            for i in self.tool[key]:
                c = copy.copy(i)
                doc_url, _ = urlparse.urldefrag(c['id'])
                c["name"] = shortname(c["id"])
                del c["id"]

                if "type" not in c:
                    raise validate.ValidationException("Missing `type` in parameter `%s`" % c["name"])

                if "default" in c and "null" not in aslist(c["type"]):
                    c["type"] = ["null"] + aslist(c["type"])
                else:
                    c["type"] = c["type"]

                if key == "inputs":
                    self.inputs_record_schema["fields"].append(c)
                elif key == "outputs":
                    self.outputs_record_schema["fields"].append(c)

        try:
            self.inputs_record_schema = schema_salad.schema.make_valid_avro(self.inputs_record_schema, {}, set())
            avro.schema.make_avsc_object(self.inputs_record_schema, self.names)
        except avro.schema.SchemaParseException as e:
            raise validate.ValidationException("Got error `%s` while prcoessing inputs of %s:\n%s" % (str(e), self.tool["id"], json.dumps(self.inputs_record_schema, indent=4)))

        try:
            self.outputs_record_schema = schema_salad.schema.make_valid_avro(self.outputs_record_schema, {}, set())
            avro.schema.make_avsc_object(self.outputs_record_schema, self.names)
        except avro.schema.SchemaParseException as e:
            raise validate.ValidationException("Got error `%s` while prcoessing outputs of %s:\n%s" % (str(e), self.tool["id"], json.dumps(self.outputs_record_schema, indent=4)))


    def _init_job(self, joborder, input_basedir, **kwargs):
        builder = Builder()
        builder.job = copy.deepcopy(joborder)

        for i in self.tool["inputs"]:
            d = shortname(i["id"])
            if d not in builder.job and "default" in i:
                builder.job[d] = i["default"]

        # Validate job order
        try:
            validate.validate_ex(self.names.get_name("input_record_schema", ""), builder.job)
        except validate.ValidationException as e:
            raise WorkflowException("Error validating input record, " + str(e))

        for r in self.requirements:
            if r["class"] not in supportedProcessRequirements:
                raise WorkflowException("Unsupported process requirement %s" % (r["class"]))

        builder.files = []
        builder.bindings = []
        builder.schemaDefs = self.schemaDefs
        builder.names = self.names
        builder.requirements = self.requirements

        dockerReq, _ = self.get_requirement("DockerRequirement")
        if dockerReq and kwargs.get("use_container"):
            builder.outdir = kwargs.get("docker_outdir") or "/tmp/job_output"
            builder.tmpdir = kwargs.get("docker_tmpdir") or "/tmp/job_tmp"
        else:
            builder.outdir = kwargs.get("outdir") or tempfile.mkdtemp()
            builder.tmpdir = kwargs.get("tmpdir") or tempfile.mkdtemp()

        builder.fs_access = kwargs.get("fs_access") or StdFsAccess(input_basedir)

        builder.bindings.extend(builder.bind_input(self.inputs_record_schema, builder.job))

        return builder


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
