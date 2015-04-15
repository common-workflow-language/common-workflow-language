import avro.schema
import json
import pprint
import copy
from flatten import flatten
import functools
import os
from pathmapper import PathMapper, DockerPathMapper
import sandboxjs
from job import CommandLineJob
import yaml
import glob
import logging
import hashlib
import random
from process import Process
from process import WorkflowException
import validate
from aslist import aslist
import expression

_logger = logging.getLogger("cwltool")

CONTENT_LIMIT = 1024 * 1024

module_dir = os.path.dirname(os.path.abspath(__file__))

supportedProcessRequirements = ("DockerRequirement",
                                "MemoryRequirement",
                                "ExpressionEngineRequirement",
                                "ScatterFeature")

class Builder(object):
    # def jseval(self, expression, context):
    #     if isinstance(expression, list):
    #         exp = "{return %s(%s);}" % (expression[0], ",".join([json.dumps(self.do_eval(e)) for e in expression[1:]]))
    #     elif expression.startswith('{'):
    #         exp = '{return function()%s();}' % (expression)
    #     else:
    #         exp = '{return %s;}' % (expression)
    #     return sandboxjs.execjs(exp, "var $job = %s; var $self = %s; %s" % (json.dumps(self.job), json.dumps(context), self.jslib))

    def bind_input(self, schema, datum):
        bindings = []

        # Handle union types
        if isinstance(schema["type"], list):
            success = False
            for t in schema["type"]:
                if t in self.schemaDefs:
                    t = self.schemaDefs[t]
                avsc = avro.schema.make_avsc_object(t, None)
                if validate.validate(avsc, datum):
                    if isinstance(t, basestring):
                        t = {"type": t}
                    bindings.extend(self.bind_input(t, datum))
                    success = True
                    break
            if not success:
                raise ValidationException("'%s' is not a valid union %s" % (datum, schema["type"]))
        elif isinstance(schema["type"], dict):
            bindings.extend(self.bind_input(schema["type"], datum))
        else:
            if schema["type"] in self.schemaDefs:
                schema = self.schemaDefs[schema["type"]]

            if schema["type"] == "record":
                for f in schema["fields"]:
                    if f["name"] in datum:
                        b = self.bind_input(f, datum[f["name"]])
                        for bi in b:
                            bi["position"].append(f["name"])
                        bindings.extend(b)

            if schema["type"] == "map":
                for v in datum:
                    b = self.bind_input(schema["values"], datum[v])
                    for bi in b:
                        bi["position"].insert(0, v)
                    bindings.extend(b)

            if schema["type"] == "array":
                for n, item in enumerate(datum):
                    b = self.bind_input({"type": schema["items"], "commandLineBinding": schema.get("commandLineBinding")}, item)
                    for bi in b:
                        bi["position"].insert(0, n)
                    bindings.extend(b)

            if schema["type"] == "File":
                if schema.get("loadContents"):
                    with open(os.path.join(self.basedir, datum["path"]), "rb") as f:
                        datum["contents"] = f.read(CONTENT_LIMIT)
                self.files.append(datum)

        b = None
        if "commandLineBinding" in schema and isinstance(schema["commandLineBinding"], dict):
            b = copy.copy(schema["commandLineBinding"])

            if b.get("position"):
                b["position"] = [b["position"]]
            else:
                b["position"] = [0]

            # Position to front of the sort key
            for bi in bindings:
                bi["position"] = b["position"] + bi["position"]

            if "valueFrom" in b:
                b["do_eval"] = b["valueFrom"]
            b["valueFrom"] = datum

            if schema["type"] == "File":
                b["is_file"] = True
            bindings.append(b)

        return bindings

    def generate_arg(self, binding):
        value = binding["valueFrom"]
        if "do_eval" in binding:
            value = expression.do_eval(binding["do_eval"], self.job, self.requirements, self.docpath, value)

        prefix = binding.get("prefix")
        sep = binding.get("separator")

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
            if sep is None or sep == " ":
                args.extend([prefix, str(j)])
            else:
                args.extend([prefix + sep + str(j)])

        return [a for a in args if a is not None]


class Tool(Process):
    def _init_job(self, joborder, basedir, **kwargs):
        # Validate job order
        try:
            validate.validate_ex(self.names.get_name("input_record_schema", ""), joborder)
        except validate.ValidationException as v:
            _logger.error("Failed to validate %s\n%s" % (pprint.pformat(joborder), v))
            raise

        for r in self.tool.get("requirements", []):
            if r["class"] not in supportedProcessRequirements:
                raise WorkflowException("Unsupported process requirement %s" % (r["class"]))

        self.requirements = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        self.hints = kwargs.get("hints", []) + self.tool.get("hints", [])

        builder = Builder()
        builder.job = copy.deepcopy(joborder)
        builder.jslib = ''
        builder.basedir = basedir
        builder.files = []
        builder.bindings = []
        builder.schemaDefs = self.schemaDefs
        builder.docpath = self.docpath

        builder.bindings.extend(builder.bind_input(self.inputs_record_schema, builder.job))

        return builder


class ExpressionTool(Tool):
    def __init__(self, toolpath_object, docpath):
        super(ExpressionTool, self).__init__(toolpath_object, "ExpressionTool", docpath)

    class ExpressionJob(object):
        def run(self, outdir=None, **kwargs):
            self.output_callback(expression.do_eval(self.script, self.builder.job, self.requirements, self.builder.docpath))

    def job(self, joborder, basedir, output_callback, **kwargs):
        builder = self._init_job(joborder, basedir, **kwargs)

        j = ExpressionTool.ExpressionJob()
        j.builder = builder
        j.script = self.tool["expression"]
        j.output_callback = output_callback
        j.requirements = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        j.hints = kwargs.get("hints", []) + self.tool.get("hints", [])

        yield j

class CommandLineTool(Tool):
    def __init__(self, toolpath_object, docpath):
        super(CommandLineTool, self).__init__(toolpath_object, "CommandLineTool", docpath)

    def job(self, joborder, basedir, output_callback, use_container=True, **kwargs):
        builder = self._init_job(joborder, basedir, **kwargs)

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

        _logger.debug(pprint.pformat(builder.bindings))
        _logger.debug(pprint.pformat(builder.files))

        reffiles = [f["path"] for f in builder.files]

        j = CommandLineJob()
        j.joborder = builder.job
        j.stdin = None
        j.stdout = None
        builder.pathmapper = None

        if self.tool.get("stdin"):
            j.stdin = self.tool["stdin"]
            if isinstance(j.stdin, dict) and "ref" in j.stdin:
                j.stdin = builder.job[j.stdin["ref"][1:]]["path"]
            reffiles.append(j.stdin)

        if self.tool.get("stdout"):
            if isinstance(self.tool["stdout"], dict) and "ref" in self.tool["stdout"]:
                for out in self.tool.get("outputs", []):
                    if out["id"] == self.tool["stdout"]["ref"]:
                        filename = self.tool["stdout"]["ref"][1:]
                        j.stdout = filename
                        out["outputBinding"] = out.get("outputBinding", {})
                        out["outputBinding"]["glob"] = filename
                if not j.stdout:
                    raise Exception("stdout refers to invalid output")
            else:
                j.stdout = self.tool["stdout"]
            if os.path.isabs(j.stdout):
                raise Exception("stdout must be a relative path")

        j.requirements = self.requirements
        j.hints = self.hints

        for r in (j.requirements + j.hints):
            if r["class"] == "DockerRequirement" and use_container:
                builder.pathmapper = DockerPathMapper(reffiles, basedir)

        if builder.pathmapper is None:
            builder.pathmapper = PathMapper(reffiles, basedir)

        for f in builder.files:
            f["path"] = builder.pathmapper.mapper(f["path"])

        builder.requirements = j.requirements

        j.generatefiles = {}
        for t in self.tool.get("fileDefs", []):
            j.generatefiles[t["filename"]] = expression.do_eval(t["value"], builder.job, j.requirements, self.docpath)

        j.environment = {}
        for t in self.tool.get("environmentDefs", []):
            j.environment[t["env"]] = expression.do_eval(t["value"], builder.job, j.requirements, self.docpath)

        j.command_line = flatten(map(builder.generate_arg, builder.bindings))

        if j.stdin:
            j.stdin = j.stdin if os.path.isabs(j.stdin) else os.path.join(basedir, j.stdin)

        j.pathmapper = builder.pathmapper
        j.collect_outputs = functools.partial(self.collect_output_ports, self.tool["outputs"], builder)
        j.output_callback = output_callback

        yield j

    def collect_output_ports(self, ports, builder, outdir):
        custom_output = os.path.join(outdir, "cwl.output.json")
        if os.path.exists(custom_output):
            outputdoc = yaml.load(custom_output)
            validate.validate_ex(self.names.get_name("output_record_schema", ""), outputdoc)
            return outputdoc
        ret = {port["id"][1:]: self.collect_output(port, builder, outdir) for port in ports}
        return ret if ret is not None else {}

    def collect_output(self, schema, builder, outdir):
        r = None
        if "outputBinding" in schema:
            binding = schema["outputBinding"]
            if "glob" in binding:
                r = [{"path": g} for g in glob.glob(os.path.join(outdir, binding["glob"]))]
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

                if schema["type"] == "array" and schema["items"] == "File":
                    pass
                elif schema["type"] == "File":
                    r = r[0] if r else None
                elif binding.get("loadContents"):
                    r = [v["contents"] for v in r]
                    if len(r) == 1:
                        r = r[0]
                else:
                    r = None

            if "valueFrom" in binding:
                r = expression.do_eval(binding["valueFrom"], builder.job, self.requirements, self.docpath, r)

        if not r and schema["type"] == "record":
            r = {}
            for f in schema["fields"]:
                r[f["name"]] = self.collect_output(f, builder, outdir)

        return r
