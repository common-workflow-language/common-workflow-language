import avro.schema
import json
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
from process import Process, shortname
from errors import WorkflowException
import schema_salad.validate as validate
from aslist import aslist
import expression
import re
import urlparse
import tempfile
from builder import CONTENT_LIMIT, substitute

_logger = logging.getLogger("cwltool")

class ExpressionTool(Process):
    def __init__(self, toolpath_object, **kwargs):
        super(ExpressionTool, self).__init__(toolpath_object, "ExpressionTool", **kwargs)

    class ExpressionJob(object):
        def run(self, **kwargs):
            try:
                self.output_callback(self.builder.do_eval(self.script), "success")
            except Exception:
                self.output_callback({}, "permanentFail")

    def job(self, joborder, input_basedir, output_callback, **kwargs):
        builder = self._init_job(joborder, input_basedir, **kwargs)

        j = ExpressionTool.ExpressionJob()
        j.builder = builder
        j.script = self.tool["expression"]
        j.output_callback = output_callback
        j.requirements = self.requirements
        j.hints = self.hints
        j.outdir = None
        j.tmpdir = None

        yield j


class CommandLineTool(Process):
    def __init__(self, toolpath_object, **kwargs):
        super(CommandLineTool, self).__init__(toolpath_object, "CommandLineTool", **kwargs)

    def makeJobRunner(self):
        return CommandLineJob()

    def makePathMapper(self, reffiles, input_basedir, **kwargs):
        dockerReq, _ = self.get_requirement("DockerRequirement")
        if dockerReq and kwargs.get("use_container"):
            return DockerPathMapper(reffiles, input_basedir)
        else:
            return PathMapper(reffiles, input_basedir)

    def job(self, joborder, input_basedir, output_callback, **kwargs):
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

        reffiles = set((f["path"] for f in builder.files))

        j = self.makeJobRunner()
        j.joborder = builder.job
        j.stdin = None
        j.stdout = None
        j.successCodes = self.tool.get("successCodes")
        j.temporaryFailCodes = self.tool.get("temporaryFailCodes")
        j.permanentFailCodes = self.tool.get("permanentFailCodes")
        j.requirements = self.requirements
        j.hints = self.hints

        _logger.debug("[job %s] initializing from %s%s",
                     id(j),
                     self.tool.get("id", ""),
                     " as part of %s" % kwargs["part_of"] if "part_of" in kwargs else "")
        _logger.debug("[job %s] %s", id(j), json.dumps(joborder, indent=4))


        builder.pathmapper = None

        if self.tool.get("stdin"):
            j.stdin = builder.do_eval(self.tool["stdin"])
            if isinstance(j.stdin, dict) and "ref" in j.stdin:
                j.stdin = builder.job[j.stdin["ref"][1:]]["path"]
            reffiles.add(j.stdin)

        if self.tool.get("stdout"):
            j.stdout = builder.do_eval(self.tool["stdout"])
            if os.path.isabs(j.stdout) or ".." in j.stdout:
                raise validate.ValidationException("stdout must be a relative path")

        builder.pathmapper = self.makePathMapper(reffiles, input_basedir, **kwargs)
        builder.requirements = j.requirements

        for f in builder.files:
            f["path"] = builder.pathmapper.mapper(f["path"])[1]

        _logger.debug("[job %s] command line bindings is %s", id(j), json.dumps(builder.bindings, indent=4))
        _logger.debug("[job %s] path mappings is %s", id(j), json.dumps({p: builder.pathmapper.mapper(p) for p in builder.pathmapper.files()}, indent=4))

        dockerReq, _ = self.get_requirement("DockerRequirement")
        if dockerReq and kwargs.get("use_container"):
            out_prefix = kwargs.get("tmp_outdir_prefix")
            j.outdir = kwargs.get("outdir") or tempfile.mkdtemp(prefix=out_prefix)
            tmpdir_prefix = kwargs.get('tmpdir_prefix')
            j.tmpdir = kwargs.get("tmpdir") or tempfile.mkdtemp(prefix=tmpdir_prefix)
        else:
            j.outdir = builder.outdir
            j.tmpdir = builder.tmpdir

        createFiles, _ = self.get_requirement("CreateFileRequirement")
        j.generatefiles = {}
        if createFiles:
            for t in createFiles["fileDef"]:
                j.generatefiles[builder.do_eval(t["filename"])] = copy.deepcopy(builder.do_eval(t["fileContent"]))

        j.environment = {}
        evr, _ = self.get_requirement("EnvVarRequirement")
        if evr:
            for t in evr["envDef"]:
                j.environment[t["envName"]] = builder.do_eval(t["envValue"])

        j.command_line = flatten(map(builder.generate_arg, builder.bindings))

        j.pathmapper = builder.pathmapper
        j.collect_outputs = functools.partial(self.collect_output_ports, self.tool["outputs"], builder)
        j.output_callback = output_callback

        yield j

    def collect_output_ports(self, ports, builder, outdir):
        try:
            custom_output = os.path.join(outdir, "cwl.output.json")
            if builder.fs_access.exists(custom_output):
                outputdoc = yaml.load(custom_output)
                validate.validate_ex(self.names.get_name("outputs_record_schema", ""), outputdoc)
                return outputdoc

            ret = {}
            for port in ports:
                fragment = shortname(port["id"])
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
                bg = builder.do_eval(binding["glob"])
                for gb in aslist(bg):
                    r.extend([{"path": g, "class": "File"} for g in builder.fs_access.glob(os.path.join(outdir, gb))])
                for files in r:
                    checksum = hashlib.sha1()
                    with builder.fs_access.open(files["path"], "rb") as f:
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
                r = builder.do_eval(binding["outputEval"], context=r)
                if schema["type"] == "File" and (not isinstance(r, dict) or "path" not in r):
                    raise WorkflowException("Expression must return a file object.")

            if schema["type"] == "File":
                if not r:
                    raise WorkflowException("No matches for output file with glob: '{}'".format(bg))
                if len(r) > 1:
                    raise WorkflowException("Multiple matches for output item that is a single file.")
                r = r[0]

            if schema["type"] == "File" and "secondaryFiles" in binding:
                r["secondaryFiles"] = []
                for sf in aslist(binding["secondaryFiles"]):
                    if isinstance(sf, dict):
                        sfpath = builder.do_eval(sf, context=r["path"])
                    else:
                        sfpath = {"path": substitute(r["path"], sf), "class": "File"}
                    if isinstance(sfpath, list):
                        r["secondaryFiles"].extend(sfpath)
                    else:
                        r["secondaryFiles"].append(sfpath)

                for sf in r["secondaryFiles"]:
                    if not builder.fs_access.exists(sf["path"]):
                        raise WorkflowException("Missing secondary file of '%s' of primary file '%s'" % (sf["path"], r["path"]))


        if not r and schema["type"] == "record":
            r = {}
            for f in schema["fields"]:
                r[f["name"]] = self.collect_output(f, builder, outdir)

        return r
