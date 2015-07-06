import job
import draft2tool
from aslist import aslist
from process import Process, WorkflowException, get_feature
import copy
import logging
import random
import os
from collections import namedtuple
import pprint
import functools
import avro_ld.validate as validate
import urlparse
import pprint
import tempfile
import shutil

_logger = logging.getLogger("cwltool")

WorkflowStateItem = namedtuple('WorkflowStateItem', ['parameter', 'value'])

def defaultMakeTool(toolpath_object, **kwargs):
    if "class" in toolpath_object:
        if toolpath_object["class"] == "CommandLineTool":
            return draft2tool.CommandLineTool(toolpath_object, **kwargs)
        elif toolpath_object["class"] == "ExpressionTool":
            return draft2tool.ExpressionTool(toolpath_object, **kwargs)
        elif toolpath_object["class"] == "Workflow":
            return Workflow(toolpath_object, **kwargs)

    raise WorkflowException("Missing or invalid 'class' field in %s, expecting one of: CommandLineTool, ExpressionTool" % toolpath_object["id"])

def findfiles(wo, fn=[]):
    if isinstance(wo, dict):
        if wo.get("class") == "File":
            fn.append(wo)
            return findfiles(wo.get("secondaryFiles", None), fn)
        else:
            for w in wo.values():
                findfiles(w, fn)
    elif isinstance(wo, list):
        for w in wo:
            findfiles(w, fn)
    return fn

class Workflow(Process):
    def __init__(self, toolpath_object, **kwargs):
        super(Workflow, self).__init__(toolpath_object, "Workflow", **kwargs)

        kwargs["requirements"] = self.requirements
        kwargs["hints"] = self.hints

        makeTool = kwargs.get("makeTool")
        self.steps = [WorkflowStep(step, **kwargs) for step in self.tool.get("steps", [])]

    def receive_output(self, step, outputparms, jobout, processStatus):
        _logger.debug("WorkflowStep completed with %s", jobout)
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

    def match_types(self, sinktype, src, iid, inputobj, linkMerge):
        if isinstance(sinktype, list):
            # Sink is union type
            for st in sinktype:
                if self.match_types(st, src, iid, inputobj, linkMerge):
                    return True
        elif isinstance(src.parameter["type"], list):
            # Source is union type
            # Check that every source type is compatible with the sink.
            for st in src.parameter["type"]:
                srccopy = copy.deepcopy(src)
                srccopy.parameter["type"] = st
                if not self.match_types(st, srccopy, iid, inputobj, linkMerge):
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

    def object_from_state(self, parms, frag_only):
        inputobj = {}
        for inp in parms:
            iid = inp["id"]
            if frag_only:
                (_, iid) = urlparse.urldefrag(iid)
                iid = iid.split(".")[-1]
            if "source" in inp:
                connections = aslist(inp["source"])
                for src in connections:
                    if src in self.state and self.state[src] is not None:
                        if not self.match_types(inp["type"], self.state[src], iid, inputobj,
                                                inp.get("linkMerge", ("merge_nested" if len(connections) > 1 else None))):
                            raise WorkflowException("Type mismatch between source '%s' (%s) and sink '%s' (%s)" % (src, self.state[src].parameter["type"], inp["id"], inp["type"]))
                    elif src not in self.state:
                        raise WorkflowException("Connect source '%s' on parameter '%s' does not exist" % (src, inp["id"]))
                    else:
                        return None
            elif "default" in inp:
                inputobj[iid] = inp["default"]
            else:
                raise WorkflowException("Value for %s not specified" % (inp["id"]))
        return inputobj

    def adjust_for_scatter(self, steps):
        (scatterSpec, _) = self.get_requirement("ScatterFeatureRequirement")
        for step in steps:
            if scatterSpec and "scatter" in step.tool:
                inputparms = copy.deepcopy(step.tool["inputs"])
                outputparms = copy.deepcopy(step.tool["outputs"])
                scatter = aslist(step.tool["scatter"])

                inp_map = {i["id"]: i for i in inputparms}
                for s in scatter:
                    if s not in inp_map:
                        raise WorkflowException("Invalid Scatter parameter '%s'" % s)

                    inp_map[s]["type"] = {"type": "array", "items": inp_map[s]["type"]}

                if step.tool.get("scatterMethod") == "nested_crossproduct":
                    nesting = len(scatter)
                else:
                    nesting = 1

                for r in xrange(0, nesting):
                    for i in outputparms:
                        i["type"] = {"type": "array", "items": i["type"]}
                step.tool["inputs"] = inputparms
                step.tool["outputs"] = outputparms

    def try_make_job(self, step, basedir, **kwargs):
        _logger.debug("Try to make job %s", step.id)

        inputparms = step.tool["inputs"]
        outputparms = step.tool["outputs"]

        try:
            inputobj = self.object_from_state(inputparms, False)
            if inputobj is None:
                return

            if step.submitted:
                return

            callback = functools.partial(self.receive_output, step, outputparms)

            (scatterSpec, _) = self.get_requirement("ScatterFeatureRequirement")
            if scatterSpec and "scatter" in step.tool:
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
            _logger.error(e)
            self.processStatus = "permanentFail"
            step.completed = True


    def job(self, joborder, basedir, output_callback, **kwargs):
        # Validate job order
        validate.validate_ex(self.names.get_name("input_record_schema", ""), joborder)

        self.adjust_for_scatter(self.steps)

        random.shuffle(self.steps)

        self.state = {}
        self.processStatus = "success"
        for i in self.tool["inputs"]:
            (_, iid) = urlparse.urldefrag(i["id"])
            if iid in joborder:
                self.state[i["id"]] = WorkflowStateItem(i, copy.deepcopy(joborder[iid]))
            elif "default" in i:
                self.state[i["id"]] = WorkflowStateItem(i, copy.deepcopy(i["default"]))
            else:
                raise WorkflowException("Input '%s' not in input object and does not have a default value." % (i["id"]))

        for s in self.steps:
            for out in s.tool["outputs"]:
                self.state[out["id"]] = None
            s.submitted = False
            s.completed = False

        if "outdir" in kwargs:
            outdir = kwargs["outdir"]
            del kwargs["outdir"]
        else:
            outdir = tempfile.mkdtemp()

        actual_jobs = []

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
                            actual_jobs.append(newjob)
                        yield newjob
            if not made_progress and completed < len(self.steps):
                yield None

        wo = self.object_from_state(self.tool["outputs"], True)

        if kwargs.get("move_outputs", True):
            targets = set()
            conflicts = set()

            for f in findfiles(wo):
                for a in actual_jobs:
                    if a.outdir and f["path"].startswith(a.outdir):
                        src = f["path"]
                        dst = os.path.join(outdir, src[len(a.outdir)+1:])
                        if dst in targets:
                            conflicts.add(dst)
                        else:
                            targets.add(dst)

            for f in findfiles(wo):
                for a in actual_jobs:
                    if a.outdir and f["path"].startswith(a.outdir):
                        src = f["path"]
                        dst = os.path.join(outdir, src[len(a.outdir)+1:])
                        if dst in conflicts:
                            sp = os.path.splitext(dst)
                            dst = "%s-%s%s" % (sp[0], str(random.randint(1, 1000000000)), sp[1])
                        dirname = os.path.dirname(dst)
                        if not os.path.exists(dirname):
                            os.makedirs(dirname)
                        _logger.info("Moving '%s' to '%s'", src, dst)
                        shutil.move(src, dst)
                        f["path"] = dst

            for a in actual_jobs:
                if a.outdir:
                    _logger.info("Removing intermediate output directory %s", a.outdir)
                    shutil.rmtree(a.outdir, True)

        output_callback(wo, self.processStatus)

class WorkflowStep(Process):
    def __init__(self, toolpath_object, **kwargs):
        try:
            makeTool = kwargs.get("makeTool")
            self.embedded_tool = makeTool(toolpath_object["run"], **kwargs)
        except validate.ValidationException as v:
            raise WorkflowException("Tool definition %s failed validation:\n%s" % (toolpath_object["run"]["id"], validate.indent(str(v))))

        if "id" in toolpath_object:
            self.id = toolpath_object["id"]
        else:
            self.id = "#step_" + str(random.randint(1, 1000000000))

        for field in ("inputs", "outputs"):
            for i in toolpath_object[field]:
                inputid = i["id"]
                (_, d) = urlparse.urldefrag(inputid)
                frag = d.split(".")[-1]
                p = urlparse.urljoin(toolpath_object["run"].get("id", self.id), "#" + frag)
                found = False
                for a in self.embedded_tool.tool[field]:
                    if a["id"] == p:
                        i.update(a)
                        found = True
                if not found:
                    raise WorkflowException("Did not find %s parameter '%s' in workflow step" % (field, p))
                i["id"] = inputid

        super(WorkflowStep, self).__init__(toolpath_object, "Process", do_validate=False, **kwargs)

        if self.embedded_tool.tool["class"] == "Workflow":
            (feature, _) = self.get_requirement("SubworkflowFeatureRequirement")
            if not feature:
                raise WorkflowException("Workflow contains embedded workflow but SubworkflowFeatureRequirement not declared")

    def receive_output(self, output_callback, jobout, processStatus):
        _logger.debug("WorkflowStep output from run is %s", jobout)
        output = {}
        for i in self.tool["outputs"]:
            (_, d) = urlparse.urldefrag(i["id"])
            field = d.split(".")[-1]
            if field in jobout:
                output[i["id"]] = jobout[field]
            else:
                processStatus = "permanentFail"
        output_callback(output, processStatus)

    def job(self, joborder, basedir, output_callback, **kwargs):
        for i in self.tool["inputs"]:
            p = i["id"]
            (_, d) = urlparse.urldefrag(p)
            field = d.split(".")[-1]
            joborder[field] = joborder[i["id"]]
            del joborder[i["id"]]

        kwargs["requirements"] = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        kwargs["hints"] = kwargs.get("hints", []) + self.tool.get("hints", [])

        _logger.info("Creating workflow step %s with input\n%s", self.id, pprint.pformat(joborder))

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
                self.processStatus = jobout["processStatus"]

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
