import job
import draft1tool
import draft2tool
from draft2tool import aslist
from process import Process
import copy
import logging
import random
from ref_resolver import from_url
import os
from collections import namedtuple
import pprint
import functools

_logger = logging.getLogger("cwltool")

WorkflowStateItem = namedtuple('WorkflowStateItem', ['parameter', 'value'])

def idk(key):
    if len(key) <= 1:
        raise Exception("Identifier is too short")
    if key[0] != '#':
        raise Exception("Must start with #")
    return key[1:]

def makeTool(toolpath_object, basedir):
    if "schema" in toolpath_object:
        return draft1tool.Tool(toolpath_object)
    elif "impl" in toolpath_object and toolpath_object.get("class", "External") == "External":
        return External(toolpath_object, basedir)
    if "class" in toolpath_object:
        if toolpath_object["class"] == "CommandLineTool":
            return draft2tool.CommandLineTool(toolpath_object)
        elif toolpath_object["class"] == "ExpressionTool":
            return draft2tool.ExpressionTool(toolpath_object)
        elif toolpath_object["class"] == "Workflow":
            return Workflow(toolpath_object)
    else:
        raise Exception("Missing 'class' field, expecting one of: Workflow, CommandLineTool, ExpressionTool, External")


class Workflow(Process):
    def __init__(self, toolpath_object):
        super(Workflow, self).__init__(toolpath_object, "Workflow")

    def receive_output(self, step, outputparms, jobout):
        _logger.info("Job got output: %s", jobout)
        for i in outputparms:
            if "id" in i:
                if idk(i["id"]) in jobout:
                    self.state[idk(i["id"])] = WorkflowStateItem(i, jobout[idk(i["id"])])
                else:
                    raise Exception("Output is missing expected field %s" % idk(i["id"]))
        step.completed = True

    def try_make_job(self, step, basedir, **kwargs):
        inputobj = {}

        if "scatter" in step.tool:
            inputparms = copy.deepcopy(step.tool["inputs"])
            outputparms = copy.deepcopy(step.tool["outputs"])
            scatter = aslist(step.tool["scatter"])
            for i in inputparms:
                if i["id"] in scatter:
                    i["type"] = {"type": "array", "items": i["type"]}

            if step.tool.get("scatterType") == "nested_crossproduct":
                nesting = len(aslist(step.tool["scatter"]))
            else:
                nesting = 1

            for r in xrange(0, nesting):
                for i in outputparms:
                    i["type"] = {"type": "array", "items": i["type"]}
        else:
            inputparms = step.tool["inputs"]
            outputparms = step.tool["outputs"]

        for inp in inputparms:
            _logger.debug(inp)
            iid = idk(inp["id"])
            if "connect" in inp:
                connections = inp["connect"]
                is_array = isinstance(inp["type"], dict) and inp["type"]["type"] == "array"
                for connection in aslist(connections):
                    src = idk(connection["source"])
                    if src in self.state:
                        if self.state[src].parameter["type"] == inp["type"]:
                            # source and input types are the same
                            if is_array and iid in inputobj:
                                # there's already a value in the input object, so extend the existing array
                                inputobj[iid].extend(self.state[src].value)
                            else:
                                # simply assign the value from state to input
                                inputobj[iid] = copy.deepcopy(self.state[src].value)
                        elif is_array and self.state[src].parameter["type"] == inp["type"]["items"]:
                            # source type is the item type on the input array
                            # promote single item to array entry
                            if iid in inputobj:
                                inputobj[iid].append(self.state[src].value)
                            else:
                                inputobj[iid] = [self.state[src].value]
                        else:
                            raise Exception("Type mismatch '%s' and '%s'" % (src, inp["id"][1:]))
                    else:
                        return
            elif "default" in inp:
                inputobj[iid] = inp["default"]
            else:
                raise Exception("Value for %s not specified" % (inp["id"]))

        _logger.info("Creating job with input: %s", inputobj)

        callback = functools.partial(self.receive_output, step, outputparms)

        if step.tool.get("scatter"):
            if step.tool.get("scatterType") == "dotproduct" or step.tool.get("scatterType") is None:
                jobs = dotproduct_scatter(step, inputobj, basedir, aslist(step.tool["scatter"]), callback, **kwargs)
            elif step.tool.get("scatterType") == "nested_crossproduct":
                jobs = nested_rossproduct_scatter(step, inputobj, basedir, aslist(step.tool["scatter"]), callback, **kwargs)
            elif step.tool.get("scatterType") == "flat_crossproduct":
                jobs = flat_crossproduct_scatter(step, inputobj, basedir, aslist(step.tool["scatter"]), callback, 0, **kwargs)
        else:
            jobs = step.job(inputobj, basedir, callback, **kwargs)

        for j in jobs:
            yield j

    def job(self, joborder, basedir, output_callback, **kwargs):
        steps = [makeTool(step, basedir) for step in self.tool.get("steps", [])]
        random.shuffle(steps)

        self.state = {}
        for i in self.tool["inputs"]:
            iid = idk(i["id"])
            if iid in joborder:
                self.state[iid] = WorkflowStateItem(i, copy.deepcopy(joborder[iid]))
            elif "default" in i:
                self.state[iid] = WorkflowStateItem(i, copy.deepcopy(i["default"]))

        for s in steps:
            s.completed = False

        completed = 0
        while completed < len(steps):
            made_progress = False
            completed = 0
            for step in steps:
                if step.completed:
                    completed += 1
                else:
                    for newjob in self.try_make_job(step, basedir, **kwargs):
                        if newjob:
                            made_progress = True
                            yield newjob
            if not made_progress:
                yield None

        wo = {}
        for i in self.tool["outputs"]:
            if "connect" in i:
                src = idk(i["connect"]["source"])
                wo[idk(i["id"])] = self.state[src].value

        output_callback(wo)

class External(Process):
    def __init__(self, toolpath_object, basedir):
        self.impl = toolpath_object["impl"]
        self.embedded_tool = makeTool(from_url(os.path.join(basedir, self.impl)), basedir)

        if "id" in toolpath_object:
            self.id = toolpath_object["id"]
        else:
            self.id = "#step_" + str(random.randint(1, 1000000000))

        for i in toolpath_object["inputs"]:
            d = i["def"][len(self.impl):]
            toolid = i.get("id", self.id + "." + idk(d))
            found = False
            for a in self.embedded_tool.tool["inputs"]:
                if a["id"] == d:
                    i.update(a)
                    found = True
            if not found:
                raise Exception("Did not find input '%s' in external process" % (i["def"]))

            i["id"] = toolid

        for i in toolpath_object["outputs"]:
            d = i["def"][len(self.impl):]
            toolid = i["id"]
            found = False
            for a in self.embedded_tool.tool["outputs"]:
                if a["id"] == d:
                    i.update(a)
                    found = True
            if not found:
                raise Exception("Did not find output '%s' in external process" % (i["def"]))

            i["id"] = toolid

        super(External, self).__init__(toolpath_object, "Process")

    def receive_output(self, jobout):
        self.output  = {}
        for i in self.tool["outputs"]:
            if i["def"][:len(self.impl)] != self.impl:
                raise Exception("'def' is '%s' but must refer to fragment of resource '%s' listed in 'impl'" % (i["def"], self.impl))
            d = idk(i["def"][len(self.impl):])
            self.output[idk(i["id"])] = jobout[d]

    def job(self, joborder, basedir, output_callback, **kwargs):
        for i in self.tool["inputs"]:
            d = i["def"][len(self.impl)+1:]
            joborder[d] = joborder[idk(i["id"])]
            del joborder[idk(i["id"])]

        self.output = None
        for t in self.embedded_tool.job(joborder, basedir, self.receive_output, **kwargs):
            yield t

        while self.output is None:
            yield None

        output_callback(self.output)


class ReceiveScatterOutput(object):
    def __init__(self, dest):
        self.dest = dest
        self.completed = 0

    def receive_scatter_output(self, index, jobout):
        for k,v in jobout.items():
            self.dest[k][index] = v
        self.completed += 1

def dotproduct_scatter(process, joborder, basedir, scatter_keys, output_callback, **kwargs):
    l = None
    for s in scatter_keys:
        if l is None:
            l = len(joborder[idk(s)])
        elif l != len(joborder[idk(s)]):
            raise Exception("Length of input arrays must be equal when performing dotproduct scatter.")

    output = {}
    for i in process.tool["outputs"]:
        output[idk(i["id"])] = [None] * l

    rc = ReceiveScatterOutput(output)

    for n in range(0, l):
        jo = copy.copy(joborder)
        for s in scatter_keys:
            jo[idk(s)] = joborder[idk(s)][n]

        for j in process.job(jo, basedir, functools.partial(rc.receive_scatter_output, n), **kwargs):
            yield j

    while rc.completed < l:
        yield None

    output_callback(output)


def nested_crossproduct_scatter(process, joborder, basedir, scatter_keys, output_callback, **kwargs):
    scatter_key = idk(scatter_keys[0])
    l = len(joborder[scatter_key])
    output = {}
    for i in process["outputs"]:
        output[idk(i["id"])] = [None] * l

    rc = ReceiveScatterOutput(output)

    for n in range(0, l):
        jo = copy.copy(joborder)
        jo[scatter_key] = joborder[scatter_key][n]

        if len(scatter_keys) == 1:
            for j in process.job(jo, basedir, functools.partial(rc.receive_scatter_output, n), **kwargs):
               yield j
        else:
            for j in nested_crossproduct_scatter(process, jo, basedir, scatter_keys[1:], functools.partial(rc.receive_scatter_output, n)):
               yield j

    while rc.completed < l:
        yield None

    output_callback(output)

def crossproduct_size(joborder, scatter_keys):
    scatter_key = idk(scatter_keys[0])
    if len(scatter_keys) == 1:
        sum = len(joborder[scatter_key])
    else:
        sum = 0
        for n in range(0, l):
            jo = copy.copy(joborder)
            jo[scatter_key] = joborder[scatter_key][n]
            sum += crossproduct_size(joborder, scatter_keys[1:])
    return sum

def flat_crossproduct_scatter(process, joborder, basedir, scatter_keys, output_callback, startindex, **kwargs):
    scatter_key = idk(scatter_keys[0])
    l = len(joborder[scatter_key])

    if startindex == 0:
        output = {}
        for i in process["outputs"]:
            output[idk(i["id"])] = [None] * crossproduct_size(joborder, scatter_keys)
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
            for j in flat_crossproduct_scatter(process, jo, basedir, scatter_keys[1:], functools.partial(rc.receive_scatter_output, put)):
                put += 1
                yield j

    if startindex == 0:
        while rc.completed < put:
            yield None

        output_callback(output)
