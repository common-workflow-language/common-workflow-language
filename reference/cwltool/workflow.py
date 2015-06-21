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

_logger = logging.getLogger("cwltool")

WorkflowStateItem = namedtuple('WorkflowStateItem', ['parameter', 'value'])

def makeTool(toolpath_object, docpath, **kwargs):
    """docpath is the directory the tool file is located."""
    if "run" in toolpath_object: # and toolpath_object.get("class", "External") == "External":
        return External(toolpath_object, docpath)
    if "class" in toolpath_object:
        if toolpath_object["class"] == "CommandLineTool":
            return draft2tool.CommandLineTool(toolpath_object, docpath, **kwargs)
        elif toolpath_object["class"] == "ExpressionTool":
            return draft2tool.ExpressionTool(toolpath_object, docpath, **kwargs)
        elif toolpath_object["class"] == "Workflow":
            return Workflow(toolpath_object, docpath, **kwargs)
    else:
        raise WorkflowException("Missing 'class' field in %s, expecting one of: CommandLineTool, ExpressionTool" % toolpath_object["id"])


class Workflow(Process):
    def __init__(self, toolpath_object, docpath, **kwargs):
        super(Workflow, self).__init__(toolpath_object, "Workflow", docpath, **kwargs)

    def receive_output(self, step, outputparms, jobout, processStatus):
        _logger.debug("WorkflowStep completed with %s", jobout)
        for i in outputparms:
            if "id" in i:
                if i["id"] in jobout:
                    self.state[i["id"]] = WorkflowStateItem(i, jobout[i["id"]])
                else:
                    raise WorkflowException("Output is missing expected field %s" % d)
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
            # Union type
            for st in sinktype:
                if self.match_types(st, src, iid, inputobj, linkMerge):
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

    def try_make_job(self, step, basedir, **kwargs):
        inputobj = {}

        _logger.debug("Try to make job %s", step.id)

        (scatterSpec, _) = get_feature("Scatter", requirements=step.tool.get("requirements"), hints=step.tool.get("hints"))
        if scatterSpec:
            inputparms = copy.deepcopy(step.tool["inputs"])
            outputparms = copy.deepcopy(step.tool["outputs"])
            scatter = aslist(scatterSpec["scatter"])

            inp_map = {i["id"]: i for i in inputparms}
            for s in scatter:
                if s not in inp_map:
                    raise WorkflowException("Invalid Scatter parameter '%s'" % s)

                inp_map[s]["type"] = {"type": "array", "items": inp_map[s]["type"]}

            if scatterSpec.get("scatterMethod") == "nested_crossproduct":
                nesting = len(scatter)
            else:
                nesting = 1

            for r in xrange(0, nesting):
                for i in outputparms:
                    i["type"] = {"type": "array", "items": i["type"]}
        else:
            inputparms = step.tool["inputs"]
            outputparms = step.tool["outputs"]

        for inp in inputparms:
            _logger.debug("Trying input %s", inp)
            iid = inp["id"]
            if "connect" in inp:
                connections = inp["connect"]
                for connection in aslist(connections):
                    src = connection["source"]
                    if src in self.state and self.state[src] is not None:
                        if not self.match_types(inp["type"], self.state[src], inp["id"], inputobj,
                                                inp.get("linkMerge", ("merge_nested" if len(connections) > 1 else None))):
                            raise WorkflowException("Type mismatch between source '%s' (%s) and sink '%s' (%s)" % (src, self.state[src].parameter["type"], inp["id"], inp["type"]))
                    elif src not in self.state:
                        raise WorkflowException("Connect source '%s' on parameter '%s' does not exist" % (src, inp["id"]))
                    else:
                        return
            elif "default" in inp:
                inputobj[iid] = inp["default"]
            else:
                raise WorkflowException("Value for %s not specified" % (inp["id"]))

        _logger.info("Creating job with input: %s", pprint.pformat(inputobj))

        callback = functools.partial(self.receive_output, step, outputparms)

        if scatterSpec:
            method = scatterSpec.get("scatterMethod")
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

        for j in jobs:
            yield j

    def job(self, joborder, basedir, output_callback, **kwargs):
        # Validate job order
        validate.validate_ex(self.names.get_name("input_record_schema", ""), joborder)

        requirements = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        hints = kwargs.get("hints", []) + self.tool.get("hints", [])

        steps = [makeTool(step, basedir) for step in self.tool.get("steps", [])]
        random.shuffle(steps)

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

        for s in steps:
            for out in s.tool["outputs"]:
                self.state[out["id"]] = None
            s.completed = False

        completed = 0
        while completed < len(steps):
            made_progress = False
            completed = 0
            for step in steps:
                if step.completed:
                    completed += 1
                else:
                    for newjob in self.try_make_job(step, basedir, requirements=requirements, hints=hints, **kwargs):
                        if newjob:
                            made_progress = True
                            yield newjob
            if not made_progress and completed < len(steps):
                yield None

        wo = {}
        for i in self.tool["outputs"]:
            if "connect" in i:
                (_, src) = urlparse.urldefrag(i['id'])
                if i["connect"]["source"] not in self.state:
                    raise WorkflowException("Connect source '%s' on parameter '%s' does not exist" % (i["connect"]["source"], inp["id"]))
                wo[src] = self.state[i["connect"]["source"]].value

        output_callback(wo, self.processStatus)

class External(Process):
    def __init__(self, toolpath_object, docpath):
        try:
            self.embedded_tool = makeTool(toolpath_object["run"], docpath)
        except validate.ValidationException as v:
            raise WorkflowException("Tool definition %s failed validation:\n%s" % (os.path.join(docpath, toolpath_object["run"]["id"]), validate.indent(str(v))))

        if "id" in toolpath_object:
            self.id = toolpath_object["id"]
        else:
            self.id = "#step_" + str(random.randint(1, 1000000000))

        for i in toolpath_object["inputs"]:
            p = i["param"] if 'param' in i else self.id
            (_, d) = urlparse.urldefrag(p)
            toolid = i.get("id", self.id + "." + d)
            found = False
            for a in self.embedded_tool.tool["inputs"]:
                if a["id"] == p:
                    i.update(a)
                    found = True
            if not found:
                raise WorkflowException("Did not find input parameter '%s' in workflow step" % (p))

            i["id"] = toolid

        for i in toolpath_object["outputs"]:
            p = i["param"] if 'param' in i else i['id']
            toolid = i["id"]
            found = False
            for a in self.embedded_tool.tool["outputs"]:
                if a["id"] == p:
                    i.update(a)
                    found = True
            if not found:
                raise WorkflowException("Did not find output parameter '%s' in workflow step" % (p))

            i["id"] = toolid

        super(External, self).__init__(toolpath_object, "WorkflowStep", docpath)

    def receive_output(self, jobout, processStatus):
        _logger.debug("WorkflowStep output from run is %s", jobout)
        self.output = {}
        for i in self.tool["outputs"]:
            (_, d) = urlparse.urldefrag(i["param"] if "param" in i else i["id"])
            self.output[i["id"]] = jobout[d]
        self.processStatus = processStatus

    def job(self, joborder, basedir, output_callback, **kwargs):
        for i in self.tool["inputs"]:
            (_, d) = urlparse.urldefrag(i["param"])
            joborder[d] = joborder[i["id"]]
            del joborder[i["id"]]

        kwargs["requirements"] = kwargs.get("requirements", []) + self.tool.get("requirements", [])
        kwargs["hints"] = kwargs.get("hints", []) + self.tool.get("hints", [])

        self.output = None
        for t in self.embedded_tool.job(joborder, basedir, self.receive_output, **kwargs):
            yield t

        while self.output is None:
            yield None

        output_callback(self.output, self.processStatus)


class ReceiveScatterOutput(object):
    def __init__(self, dest):
        self.dest = dest
        self.completed = 0
        self.processStatus = "success"

    def receive_scatter_output(self, index, jobout, processStatus):
        for k,v in jobout.items():
            self.dest[k][index] = v

        if processStatus != "success":
            if self.processStatus != "permanentFail":
                self.processStatus = jobout["processStatus"]

        self.completed += 1

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

    rc = ReceiveScatterOutput(output)

    for n in range(0, l):
        jo = copy.copy(joborder)
        for s in scatter_keys:
            jo[s] = joborder[s][n]

        for j in process.job(jo, basedir, functools.partial(rc.receive_scatter_output, n), **kwargs):
            yield j

    while rc.completed < l:
        yield None

    output_callback(output, rc.processStatus)


def nested_crossproduct_scatter(process, joborder, basedir, scatter_keys, output_callback, **kwargs):
    scatter_key = scatter_keys[0]
    l = len(joborder[scatter_key])
    output = {}
    for i in process.tool["outputs"]:
        output[i["id"]] = [None] * l

    rc = ReceiveScatterOutput(output)

    for n in range(0, l):
        jo = copy.copy(joborder)
        jo[scatter_key] = joborder[scatter_key][n]

        if len(scatter_keys) == 1:
            for j in process.job(jo, basedir, functools.partial(rc.receive_scatter_output, n), **kwargs):
               yield j
        else:
            for j in nested_crossproduct_scatter(process, jo, basedir, scatter_keys[1:], functools.partial(rc.receive_scatter_output, n), **kwargs):
               yield j

    while rc.completed < l:
        yield None

    output_callback(output, rc.processStatus)

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
        rc = ReceiveScatterOutput(output)
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
                put += 1
                yield j

    if startindex == 0 and not isinstance(output_callback, ReceiveScatterOutput):
        while rc.completed < put:
            yield None

        output_callback(output, rc.processStatus)
