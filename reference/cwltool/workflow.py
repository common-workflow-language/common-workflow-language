import job
import draft2tool
from aslist import aslist
from process import Process, get_feature, empty_subtree, shortname
from errors import WorkflowException
import copy
import logging
import random
import os
from collections import namedtuple
import pprint
import functools
import schema_salad.validate as validate
import urlparse
import pprint
import tempfile
import shutil
import json

_logger = logging.getLogger("cwltool")

WorkflowStateItem = namedtuple('WorkflowStateItem', ['parameter', 'value'])

def defaultMakeTool(toolpath_object, **kwargs):
    if not isinstance(toolpath_object, dict):
        raise WorkflowException("Not a dict: `%s`" % toolpath_object)
    if "class" in toolpath_object:
        if toolpath_object["class"] == "CommandLineTool":
            return draft2tool.CommandLineTool(toolpath_object, **kwargs)
        elif toolpath_object["class"] == "ExpressionTool":
            return draft2tool.ExpressionTool(toolpath_object, **kwargs)
        elif toolpath_object["class"] == "Workflow":
            return Workflow(toolpath_object, **kwargs)

    raise WorkflowException("Missing or invalid 'class' field in %s, expecting one of: CommandLineTool, ExpressionTool, Workflow" % toolpath_object["id"])

def findfiles(wo, fn=None):
    if fn is None:
        fn = []
    if isinstance(wo, dict):
        if wo.get("class") == "File":
            fn.append(wo)
            findfiles(wo.get("secondaryFiles", None), fn)
        else:
            for w in wo.values():
                findfiles(w, fn)
    elif isinstance(wo, list):
        for w in wo:
            findfiles(w, fn)
    return fn


def match_types(sinktype, src, iid, inputobj, linkMerge):
    if isinstance(sinktype, list):
        # Sink is union type
        for st in sinktype:
            if match_types(st, src, iid, inputobj, linkMerge):
                return True
    elif isinstance(src.parameter["type"], list):
        # Source is union type
        # Check that every source type is compatible with the sink.
        for st in src.parameter["type"]:
            srccopy = copy.deepcopy(src)
            srccopy.parameter["type"] = st
            if not match_types(st, srccopy, iid, inputobj, linkMerge):
                return False
        return True
    else:
        is_array = isinstance(sinktype, dict) and sinktype["type"] == "array"
        if is_array and linkMerge:
            if iid not in inputobj:
                inputobj[iid] = []
            if linkMerge == "merge_nested":
                inputobj[iid].append(src.value)
            elif linkMerge == "merge_flattened":
                if isinstance(src.value, list):
                    inputobj[iid].extend(src.value)
                else:
                    inputobj[iid].append(src.value)
            else:
                raise WorkflowException("Unrecognized linkMerge enum '%s'" % linkMerge)
            return True
        elif src.parameter["type"] == sinktype:
            # simply assign the value from state to input
            inputobj[iid] = copy.deepcopy(src.value)
            return True
    return False


def object_from_state(state, parms, frag_only, supportsMultipleInput):
    inputobj = {}
    for inp in parms:
        iid = inp["id"]
        if frag_only:
            iid = shortname(iid)
        if "source" in inp:
            if isinstance(inp["source"], list) and not supportsMultipleInput:
                raise WorkflowException("Workflow contains multiple inbound links to a single parameter but MultipleInputFeatureRequirement is not declared.")
            connections = aslist(inp["source"])
            for src in connections:
                if src in state and state[src] is not None:
                    if not match_types(inp["type"], state[src], iid, inputobj,
                                            inp.get("linkMerge", ("merge_nested" if len(connections) > 1 else None))):
                        raise WorkflowException("Type mismatch between source '%s' (%s) and sink '%s' (%s)" % (src, state[src].parameter["type"], inp["id"], inp["type"]))
                elif src not in state:
                    raise WorkflowException("Connect source '%s' on parameter '%s' does not exist" % (src, inp["id"]))
                else:
                    return None
        elif "default" in inp:
            inputobj[iid] = inp["default"]
        else:
            raise WorkflowException("Value for %s not specified" % (inp["id"]))
    return inputobj


class WorkflowJobStep(object):
    def __init__(self, step):
        self.step = step
        self.tool = step.tool
        self.id = step.id
        self.submitted = False
        self.completed = False

    def job(self, joborder, basedir, output_callback, **kwargs):
        kwargs["part_of"] = "step %s" % id(self)
        for j in self.step.job(joborder, basedir, output_callback, **kwargs):
            yield j

class WorkflowJob(object):
    def __init__(self, workflow, **kwargs):
        self.workflow = workflow
        self.tool = workflow.tool
        self.steps = [WorkflowJobStep(s) for s in workflow.steps]
        self.id = workflow.tool["id"]
        if "outdir" in kwargs:
            self.outdir = kwargs["outdir"]
        elif "tmp_outdir_prefix" in kwargs:
            self.outdir = tempfile.mkdtemp(prefix=kwargs["tmp_outdir_prefix"])
        else:
            # tmp_outdir_prefix defaults to tmp, so this is unlikely to be used
            self.outdir = tempfile.mkdtemp()

        _logger.debug("[workflow %s] initialized from %s", id(self), self.tool["id"])

    def receive_output(self, step, outputparms, jobout, processStatus):
        _logger.debug("[workflow %s] step %s completed", id(self), id(step))
        for i in outputparms:
            if "id" in i:
                if i["id"] in jobout:
                    self.state[i["id"]] = WorkflowStateItem(i, jobout[i["id"]])
                else:
                    _logger.error("Output is missing expected field %s" % i["id"])
                    processStatus = "permanentFail"

        if processStatus != "success":
            if self.processStatus != "permanentFail":
                self.processStatus = processStatus

            if processStatus == "success":
                _logger.info("Workflow step %s completion status is %s", step.id, processStatus)
            else:
                _logger.warn("Workflow step %s completion status is %s", step.id, processStatus)

        step.completed = True

    def try_make_job(self, step, basedir, **kwargs):
        inputparms = step.tool["inputs"]
        outputparms = step.tool["outputs"]

        supportsMultipleInput = bool(self.workflow.get_requirement("MultipleInputFeatureRequirement")[0])

        try:
            inputobj = object_from_state(self.state, inputparms, False, supportsMultipleInput)
            if inputobj is None:
                _logger.debug("[workflow %s] job step %s not ready", id(self), step.id)
                return

            _logger.debug("[step %s] starting job step %s of workflow %s", id(step), step.id, id(self))

            if step.submitted:
                return

            callback = functools.partial(self.receive_output, step, outputparms)

            if "scatter" in step.tool:
                scatter = aslist(step.tool["scatter"])
                method = step.tool.get("scatterMethod")
                if method is None and len(scatter) != 1:
                    raise WorkflowException("Must specify scatterMethod when scattering over multiple inputs")

                if method == "dotproduct" or method is None:
                    jobs = dotproduct_scatter(step, inputobj, basedir, scatter, callback, **kwargs)
                elif method == "nested_crossproduct":
                    jobs = nested_crossproduct_scatter(step, inputobj, basedir, scatter, callback, **kwargs)
                elif method == "flat_crossproduct":
                    jobs = flat_crossproduct_scatter(step, inputobj, basedir, scatter, callback, 0, **kwargs)
            else:
                jobs = step.job(inputobj, basedir, callback, **kwargs)

            step.submitted = True

            for j in jobs:
                yield j
        except Exception as e:
            _logger.exception("Unhandled exception")
            self.processStatus = "permanentFail"
            step.completed = True

    def run(self, **kwargs):
        _logger.debug("[workflow %s] starting", id(self))

    def job(self, joborder, basedir, output_callback, move_outputs=True, **kwargs):
        self.state = {}
        self.processStatus = "success"

        if "outdir" in kwargs:
            del kwargs["outdir"]

        for i in self.tool["inputs"]:
            iid = shortname(i["id"])
            if iid in joborder:
                self.state[i["id"]] = WorkflowStateItem(i, copy.deepcopy(joborder[iid]))
            elif "default" in i:
                self.state[i["id"]] = WorkflowStateItem(i, copy.deepcopy(i["default"]))
            else:
                raise WorkflowException("Input '%s' not in input object and does not have a default value." % (i["id"]))

        for s in self.steps:
            for out in s.tool["outputs"]:
                self.state[out["id"]] = None

        output_dirs = set()

        completed = 0
        while completed < len(self.steps) and self.processStatus == "success":
            made_progress = False
            completed = 0
            for step in self.steps:
                if step.completed:
                    completed += 1
                else:
                    for newjob in self.try_make_job(step, basedir, **kwargs):
                        if newjob:
                            made_progress = True
                            if newjob.outdir:
                                output_dirs.add(newjob.outdir)
                        yield newjob
            if not made_progress and completed < len(self.steps):
                yield None

        supportsMultipleInput = bool(self.workflow.get_requirement("MultipleInputFeatureRequirement")[0])

        wo = object_from_state(self.state, self.tool["outputs"], True, supportsMultipleInput)

        if move_outputs:
            targets = set()
            conflicts = set()

            outfiles = findfiles(wo)

            for f in outfiles:
                for a in output_dirs:
                    if f["path"].startswith(a):
                        src = f["path"]
                        dst = os.path.join(self.outdir, src[len(a)+1:])
                        if dst in targets:
                            conflicts.add(dst)
                        else:
                            targets.add(dst)

            for f in outfiles:
                for a in output_dirs:
                    if f["path"].startswith(a):
                        src = f["path"]
                        dst = os.path.join(self.outdir, src[len(a)+1:])
                        if dst in conflicts:
                            sp = os.path.splitext(dst)
                            dst = "%s-%s%s" % (sp[0], str(random.randint(1, 1000000000)), sp[1])
                        dirname = os.path.dirname(dst)
                        if not os.path.exists(dirname):
                            os.makedirs(dirname)
                        _logger.debug("[workflow %s] Moving '%s' to '%s'", id(self), src, dst)
                        shutil.move(src, dst)
                        f["path"] = dst

            for a in output_dirs:
                if os.path.exists(a) and empty_subtree(a):
                    _logger.debug("[workflow %s] Removing intermediate output directory %s", id(self), a)
                    shutil.rmtree(a, True)

        _logger.info("[workflow %s] outdir is %s", id(self), self.outdir)

        output_callback(wo, self.processStatus)


class Workflow(Process):
    def __init__(self, toolpath_object, **kwargs):
        super(Workflow, self).__init__(toolpath_object, "Workflow", **kwargs)

        kwargs["requirements"] = self.requirements
        kwargs["hints"] = self.hints

        makeTool = kwargs.get("makeTool")
        self.steps = [WorkflowStep(step, n, **kwargs) for n,step in enumerate(self.tool.get("steps", []))]
        random.shuffle(self.steps)

        # TODO: statically validate data links instead of doing it at runtime.

    def job(self, joborder, basedir, output_callback, **kwargs):
        builder = self._init_job(joborder, basedir, **kwargs)

        kwargs["part_of"] = "workflow %s" % (id(self))
        wj = WorkflowJob(self, **kwargs)

        yield wj

        for w in wj.job(builder.job, basedir, output_callback, **kwargs):
            yield w


class WorkflowStep(Process):
    def __init__(self, toolpath_object, pos, **kwargs):
        try:
            makeTool = kwargs.get("makeTool")
            self.embedded_tool = makeTool(toolpath_object["run"], **kwargs)
        except validate.ValidationException as v:
            raise WorkflowException("Tool definition %s failed validation:\n%s" % (toolpath_object["run"]["id"], validate.indent(str(v))))

        if "id" in toolpath_object:
            self.id = toolpath_object["id"]
        else:
            self.id = "#step" + str(pos)

        for field in ("inputs", "outputs"):
            for i in toolpath_object[field]:
                inputid = i["id"]
                p = shortname(inputid)
                found = False
                for a in self.embedded_tool.tool[field]:
                    frag = shortname(a["id"])
                    if frag == p:
                        i.update(a)
                        found = True
                if not found:
                    raise WorkflowException("Parameter '%s' of %s in workflow step %s does not correspond to parameter in %s" % (p, field, self.id, self.embedded_tool.tool.get("id")))
                i["id"] = inputid

        super(WorkflowStep, self).__init__(toolpath_object, "Process", do_validate=False, **kwargs)

        if self.embedded_tool.tool["class"] == "Workflow":
            (feature, _) = self.get_requirement("SubworkflowFeatureRequirement")
            if not feature:
                raise WorkflowException("Workflow contains embedded workflow but SubworkflowFeatureRequirement not declared")

        if "scatter" in self.tool:
            (feature, _) = self.get_requirement("ScatterFeatureRequirement")
            if not feature:
                raise WorkflowException("Workflow contains scatter but ScatterFeatureRequirement not declared")

            inputparms = copy.deepcopy(self.tool["inputs"])
            outputparms = copy.deepcopy(self.tool["outputs"])
            scatter = aslist(self.tool["scatter"])

            method = self.tool.get("scatterMethod")
            if method is None and len(scatter) != 1:
                raise WorkflowException("Must specify scatterMethod when scattering over multiple inputs")

            inp_map = {i["id"]: i for i in inputparms}
            for s in scatter:
                if s not in inp_map:
                    raise WorkflowException("Invalid Scatter parameter '%s'" % s)

                inp_map[s]["type"] = {"type": "array", "items": inp_map[s]["type"]}

            if self.tool.get("scatterMethod") == "nested_crossproduct":
                nesting = len(scatter)
            else:
                nesting = 1

            for r in xrange(0, nesting):
                for i in outputparms:
                    i["type"] = {"type": "array", "items": i["type"]}
            self.tool["inputs"] = inputparms
            self.tool["outputs"] = outputparms

    def receive_output(self, output_callback, jobout, processStatus):
        #_logger.debug("WorkflowStep output from run is %s", jobout)
        output = {}
        for i in self.tool["outputs"]:
            field = shortname(i["id"])
            if field in jobout:
                output[i["id"]] = jobout[field]
            else:
                processStatus = "permanentFail"
        output_callback(output, processStatus)

    def job(self, joborder, basedir, output_callback, **kwargs):
        for i in self.tool["inputs"]:
            p = i["id"]
            field = shortname(p)
            joborder[field] = joborder[i["id"]]
            del joborder[i["id"]]

        kwargs["requirements"] = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        kwargs["hints"] = kwargs.get("hints", []) + self.tool.get("hints", [])

        for t in self.embedded_tool.job(joborder, basedir, functools.partial(self.receive_output, output_callback), **kwargs):
            yield t


class ReceiveScatterOutput(object):
    def __init__(self, output_callback, dest):
        self.dest = dest
        self.completed = 0
        self.processStatus = "success"
        self.total = None
        self.output_callback = output_callback

    def receive_scatter_output(self, index, jobout, processStatus):
        for k,v in jobout.items():
            self.dest[k][index] = v

        if processStatus != "success":
            if self.processStatus != "permanentFail":
                self.processStatus = processStatus

        self.completed += 1

        if self.completed == self.total:
            self.output_callback(self.dest, self.processStatus)

    def setTotal(self, total):
        self.total = total
        if self.completed == self.total:
            self.output_callback(self.dest, self.processStatus)


def dotproduct_scatter(process, joborder, basedir, scatter_keys, output_callback, **kwargs):
    l = None
    for s in scatter_keys:
        if l is None:
            l = len(joborder[s])
        elif l != len(joborder[s]):
            raise WorkflowException("Length of input arrays must be equal when performing dotproduct scatter.")

    output = {}
    for i in process.tool["outputs"]:
        output[i["id"]] = [None] * l

    rc = ReceiveScatterOutput(output_callback, output)

    for n in range(0, l):
        jo = copy.copy(joborder)
        for s in scatter_keys:
            jo[s] = joborder[s][n]

        for j in process.job(jo, basedir, functools.partial(rc.receive_scatter_output, n), **kwargs):
            yield j

    rc.setTotal(l)


def nested_crossproduct_scatter(process, joborder, basedir, scatter_keys, output_callback, **kwargs):
    scatter_key = scatter_keys[0]
    l = len(joborder[scatter_key])
    output = {}
    for i in process.tool["outputs"]:
        output[i["id"]] = [None] * l

    rc = ReceiveScatterOutput(output_callback, output)

    for n in range(0, l):
        jo = copy.copy(joborder)
        jo[scatter_key] = joborder[scatter_key][n]

        if len(scatter_keys) == 1:
            for j in process.job(jo, basedir, functools.partial(rc.receive_scatter_output, n), **kwargs):
                yield j
        else:
            for j in nested_crossproduct_scatter(process, jo, basedir, scatter_keys[1:], functools.partial(rc.receive_scatter_output, n), **kwargs):
                yield j

    rc.setTotal(l)


def crossproduct_size(joborder, scatter_keys):
    scatter_key = scatter_keys[0]
    if len(scatter_keys) == 1:
        sum = len(joborder[scatter_key])
    else:
        sum = 0
        for n in range(0, len(joborder[scatter_key])):
            jo = copy.copy(joborder)
            jo[scatter_key] = joborder[scatter_key][n]
            sum += crossproduct_size(joborder, scatter_keys[1:])
    return sum

def flat_crossproduct_scatter(process, joborder, basedir, scatter_keys, output_callback, startindex, **kwargs):
    scatter_key = scatter_keys[0]
    l = len(joborder[scatter_key])

    if startindex == 0 and not isinstance(output_callback, ReceiveScatterOutput):
        output = {}
        for i in process.tool["outputs"]:
            output[i["id"]] = [None] * crossproduct_size(joborder, scatter_keys)
        rc = ReceiveScatterOutput(output_callback, output)
    else:
        rc = output_callback

    put = startindex
    for n in range(0, l):
        jo = copy.copy(joborder)
        jo[scatter_key] = joborder[scatter_key][n]

        if len(scatter_keys) == 1:
            for j in process.job(jo, basedir, functools.partial(rc.receive_scatter_output, put), **kwargs):
                yield j
            put += 1
        else:
            for j in flat_crossproduct_scatter(process, jo, basedir, scatter_keys[1:], rc, put, **kwargs):
                if j:
                    put += 1
                yield j

    rc.setTotal(put)
