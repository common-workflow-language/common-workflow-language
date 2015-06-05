import avro.schema
import json
import pprint
import copy
from flatten import flatten
import functools
import os
from pathmapper import PathMapper, DockerPathMapper
from job import CommandLineJob
import yaml
import glob
import logging
import hashlib
import random
from process import Process
from process import WorkflowException
from process import get_feature
import avro_ld.validate as validate
from aslist import aslist
import expression
import re
import urlparse

_logger = logging.getLogger("cwltool")

CONTENT_LIMIT = 64 * 1024

module_dir = os.path.dirname(os.path.abspath(__file__))

supportedProcessRequirements = ("DockerRequirement",
                                "MemoryRequirement",
                                "ExpressionEngineRequirement",
                                "Scatter",
                                "SchemaDefRequirement",
                                "EnvVarRequirement",
                                "CreateFileRequirement")

def substitute(value, replace):
    if replace[0] == "^":
        return substitute(value[0:value.rindex('.')], replace[1:])
    else:
        return value + replace

class Builder(object):

    def bind_input(self, schema, datum, lead_pos=[], tail_pos=[]):
        bindings = []
        binding = None
        if "inputBinding" in schema and isinstance(schema["inputBinding"], dict):
            binding = copy.copy(schema["inputBinding"])

            if "position" in binding:
                binding["position"] = aslist(lead_pos) + aslist(binding["position"]) + aslist(tail_pos)
            else:
                binding["position"] = aslist(lead_pos) + [0] + aslist(tail_pos)

            if "valueFrom" in binding:
                binding["do_eval"] = binding["valueFrom"]
            binding["valueFrom"] = datum

            if schema["type"] == "File":
                binding["is_file"] = True

        # Handle union types
        if isinstance(schema["type"], list):
            for t in schema["type"]:
                if isinstance(t, basestring) and self.names.has_name(t, ""):
                    avsc = self.names.get_name(t, "")
                else:
                    avsc = avro.schema.make_avsc_object(t, self.names)
                if validate.validate(avsc, datum):
                    schema = copy.deepcopy(schema)
                    schema["type"] = t
                    return self.bind_input(schema, datum, lead_pos=lead_pos, tail_pos=tail_pos)
            raise ValidationException("'%s' is not a valid union %s" % (datum, schema["type"]))
        elif isinstance(schema["type"], dict):
            st = copy.deepcopy(schema["type"])
            if binding and "inputBinding" not in st and "itemSeparator" not in binding and st["type"] in ("array", "map"):
                st["inputBinding"] = {}
            bindings.extend(self.bind_input(st, datum, lead_pos=lead_pos, tail_pos=tail_pos))
        else:
            if schema["type"] in self.schemaDefs:
                schema = self.schemaDefs[schema["type"]]

            if schema["type"] == "record":
                for f in schema["fields"]:
                    if f["name"] in datum:
                        bindings.extend(self.bind_input(f, datum[f["name"]], lead_pos=lead_pos, tail_pos=f["name"]))

            if schema["type"] == "map":
                for n, item in datum.items():
                    b2 = None
                    if binding:
                        b2 = copy.deepcopy(binding)
                        b2["valueFrom"] = [n, item]
                    bindings.extend(self.bind_input({"type": schema["values"], "inputBinding": b2},
                                                    item, lead_pos=n, tail_pos=tail_pos))
                binding = None

            if schema["type"] == "array":
                for n, item in enumerate(datum):
                    b2 = None
                    if binding:
                        b2 = copy.deepcopy(binding)
                        b2["valueFrom"] = item
                    bindings.extend(self.bind_input({"type": schema["items"], "inputBinding": b2},
                                                    item, lead_pos=n, tail_pos=tail_pos))
                binding = None

            if schema["type"] == "File":
                self.files.append(datum)
                if binding:
                    if binding.get("loadContents"):
                        with open(os.path.join(self.input_basedir, datum["path"]), "rb") as f:
                            datum["contents"] = f.read(CONTENT_LIMIT)

                    if "secondaryFiles" in binding:
                        if "secondaryFiles" not in datum:
                            datum["secondaryFiles"] = []
                        for sf in aslist(schema["secondaryFiles"]):
                            if isinstance(sf, dict):
                                sfpath = expression.do_eval(sf, self.job, self.requirements, self.docpath, datum["path"])
                            else:
                                sfpath = {"path": substitute(datum["path"], sf)}
                            if isinstance(sfpath, list):
                                datum["secondaryFiles"].extend(sfpath)
                            else:
                                datum["secondaryFiles"].append(sfpath)
                            self.files.append(sfpath)

        # Position to front of the sort key
        if binding:
            for bi in bindings:
                bi["position"] = binding["position"] + bi["position"]
            bindings.append(binding)

        return bindings

    def generate_arg(self, binding):
        value = binding["valueFrom"]
        if "do_eval" in binding:
            value = expression.do_eval(binding["do_eval"], self.job, self.requirements, self.docpath, value)

        prefix = binding.get("prefix")
        sep = binding.get("separate", True)

        l = []
        if isinstance(value, list):
            if binding.get("itemSeparator"):
                l = [binding["itemSeparator"].join([str(v) for v in value])]
            elif binding.get("do_eval"):
                return ([prefix] if prefix else []) + value
            elif prefix:
                return [prefix]
            else:
                return []
        elif binding.get("is_file"):
            l = [value["path"]]
        elif isinstance(value, dict):
            return [prefix] if prefix else []
        elif value is True and prefix:
            return [prefix]
        elif value is False or value is None:
            return []
        else:
            l = [value]

        args = []
        for j in l:
            if sep:
                args.extend([prefix, str(j)])
            else:
                args.append(prefix + str(j))

        return [a for a in args if a is not None]


class Tool(Process):
    def _init_job(self, joborder, input_basedir, **kwargs):
        builder = Builder()
        builder.job = copy.deepcopy(joborder)

        for i in self.tool["inputs"]:
            (_, d) = urlparse.urldefrag(i["id"])
            if d not in builder.job and "default" in i:
                builder.job[d] = i["default"]

        # Validate job order
        try:
            validate.validate_ex(self.names.get_name("input_record_schema", ""), builder.job)
        except validate.ValidationException as e:
            raise WorkflowException("Error validating input record, " + str(e))

        for r in self.tool.get("requirements", []):
            if r["class"] not in supportedProcessRequirements:
                raise WorkflowException("Unsupported process requirement %s" % (r["class"]))

        self.requirements = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        self.hints = kwargs.get("hints", []) + self.tool.get("hints", [])

        builder.input_basedir = input_basedir
        builder.files = []
        builder.bindings = []
        builder.schemaDefs = self.schemaDefs
        builder.docpath = self.docpath
        builder.names = self.names

        builder.bindings.extend(builder.bind_input(self.inputs_record_schema, builder.job))

        return builder


class ExpressionTool(Tool):
    def __init__(self, toolpath_object, docpath, **kwargs):
        super(ExpressionTool, self).__init__(toolpath_object, "ExpressionTool", docpath, **kwargs)

    class ExpressionJob(object):
        def run(self, outdir=None, **kwargs):
            try:
                self.output_callback(expression.do_eval(self.script, self.builder.job, self.requirements, self.builder.docpath), "success")
            except Exception:
                self.output_callback({}, "permanentFail")

    def job(self, joborder, input_basedir, output_callback, **kwargs):
        builder = self._init_job(joborder, input_basedir, **kwargs)

        j = ExpressionTool.ExpressionJob()
        j.builder = builder
        j.script = self.tool["expression"]
        j.output_callback = output_callback
        j.requirements = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        j.hints = kwargs.get("hints", []) + self.tool.get("hints", [])

        yield j

class CommandLineTool(Tool):
    def __init__(self, toolpath_object, docpath, **kwargs):
        super(CommandLineTool, self).__init__(toolpath_object, "CommandLineTool", docpath, **kwargs)

    def job(self, joborder, input_basedir, output_callback, use_container=True, **kwargs):
        builder = self._init_job(joborder, input_basedir, **kwargs)

        if self.tool["baseCommand"]:
            for n, b in enumerate(aslist(self.tool["baseCommand"])):
                builder.bindings.append({
                    "position": [-1000000, n],
                    "valueFrom": b
                })

        if self.tool.get("arguments"):
            for i, a in enumerate(self.tool["arguments"]):
                if isinstance(a, dict):
                    a = copy.copy(a)
                    if a.get("position"):
                        a["position"] = [a["position"], i]
                    else:
                        a["position"] = [0, i]
                    a["do_eval"] = a["valueFrom"]
                    a["valueFrom"] = None
                    builder.bindings.append(a)
                else:
                    builder.bindings.append({
                        "position": [0, i],
                        "valueFrom": a
                    })

        builder.bindings.sort(key=lambda a: a["position"])

        reffiles = [f["path"] for f in builder.files]

        j = CommandLineJob()
        j.joborder = builder.job
        j.stdin = None
        j.stdout = None
        j.successCodes = self.tool.get("successCodes")
        j.temporaryFailCodes = self.tool.get("temporaryFailCodes")
        j.permanentFailCodes = self.tool.get("permanentFailCodes")
        j.requirements = self.requirements
        j.hints = self.hints

        builder.pathmapper = None

        if self.tool.get("stdin"):
            j.stdin = expression.do_eval(self.tool["stdin"], builder.job, self.requirements, self.docpath, j.stdin)
            if isinstance(j.stdin, dict) and "ref" in j.stdin:
                j.stdin = builder.job[j.stdin["ref"][1:]]["path"]
            reffiles.append(j.stdin)

        if self.tool.get("stdout"):
            j.stdout = expression.do_eval(self.tool["stdout"], builder.job, j.requirements, self.docpath)
            if os.path.isabs(j.stdout):
                raise validate.ValidationException("stdout must be a relative path")

        dockerReq, _ = get_feature("DockerRequirement", requirements=self.requirements, hints=self.hints)
        if dockerReq and use_container:
                builder.pathmapper = DockerPathMapper(reffiles, input_basedir)

        if builder.pathmapper is None:
            builder.pathmapper = PathMapper(reffiles, input_basedir)

        for f in builder.files:
            f["path"] = builder.pathmapper.mapper(f["path"])[1]

        _logger.debug("Bindings is %s", pprint.pformat(builder.bindings))
        _logger.debug("Files is %s", pprint.pformat({p: builder.pathmapper.mapper(p) for p in builder.pathmapper.files()}))

        builder.requirements = j.requirements

        j.generatefiles = {}
        createFiles, _ = get_feature("CreateFileRequirement", requirements=self.requirements, hints=self.hints)
        if createFiles:
            for t in createFiles["fileDef"]:
                j.generatefiles[t["filename"]] = expression.do_eval(t["fileContent"], builder.job, j.requirements, self.docpath)

        j.environment = {}
        evr, _ = get_feature("EnvVarRequirement", requirements=self.requirements, hints=self.hints)
        if evr:
            for t in evr["envDef"]:
                j.environment[t["envName"]] = expression.do_eval(t["envValue"], builder.job, j.requirements, self.docpath)

        j.command_line = flatten(map(builder.generate_arg, builder.bindings))

        if j.stdin:
            j.stdin = j.stdin if os.path.isabs(j.stdin) else os.path.join(input_basedir, j.stdin)

        j.pathmapper = builder.pathmapper
        j.collect_outputs = functools.partial(self.collect_output_ports, self.tool["outputs"], builder)
        j.output_callback = output_callback

        yield j

    def collect_output_ports(self, ports, builder, outdir):
        try:
            custom_output = os.path.join(outdir, "cwl.output.json")
            if os.path.exists(custom_output):
                outputdoc = yaml.load(custom_output)
                validate.validate_ex(self.names.get_name("outputs_record_schema", ""), outputdoc)
                return outputdoc

            ret = {}
            for port in ports:
                doc_url, fragment = urlparse.urldefrag(port['id'])
                ret[fragment] = self.collect_output(port, builder, outdir)
            validate.validate_ex(self.names.get_name("outputs_record_schema", ""), ret)
            return ret if ret is not None else {}
        except validate.ValidationException as e:
            raise WorkflowException("Error validating output record, " + str(e) + "\n in " + json.dumps(ret, indent=4))

    def collect_output(self, schema, builder, outdir):
        r = None
        if "outputBinding" in schema:
            binding = schema["outputBinding"]
            if "glob" in binding:
                r = []
                bg = expression.do_eval(binding["glob"], builder.job, self.requirements, self.docpath)
                for gb in aslist(bg):
                    r.extend([{"path": g, "class": "File"} for g in glob.glob(os.path.join(outdir, gb))])
                for files in r:
                    checksum = hashlib.sha1()
                    with open(files["path"], "rb") as f:
                        contents = f.read(CONTENT_LIMIT)
                        if binding.get("loadContents"):
                            files["contents"] = contents
                        filesize = 0
                        while contents != "":
                            checksum.update(contents)
                            filesize += len(contents)
                            contents = f.read(1024*1024)
                    files["checksum"] = "sha1$%s" % checksum.hexdigest()
                    files["size"] = filesize

            if "outputEval" in binding:
                r = expression.do_eval(binding["outputEval"], builder.job, self.requirements, self.docpath, r)
                if schema["type"] == "File" and (not isinstance(r, dict) or "path" not in r):
                    raise WorkflowException("Expression must return a file object.")

            if schema["type"] == "File":
                if len(r) != 1:
                    raise WorkflowException("Multiple matches for output item that is a single file.")
                r = r[0]

            if schema["type"] == "File" and "secondaryFiles" in binding:
                r["secondaryFiles"] = []
                for sf in aslist(binding["secondaryFiles"]):
                    if isinstance(sf, dict):
                        sfpath = expression.do_eval(sf, self.job, self.requirements, self.docpath, r["path"])
                    else:
                        sfpath = {"path": substitute(r["path"], sf)}
                    if isinstance(sfpath, list):
                        r["secondaryFiles"].extend(sfpath)
                    else:
                        r["secondaryFiles"].append(sfpath)


        if not r and schema["type"] == "record":
            r = {}
            for f in schema["fields"]:
                r[f["name"]] = self.collect_output(f, builder, outdir)

        return r
