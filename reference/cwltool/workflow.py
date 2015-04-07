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


class WorkflowJob(object):
    def try_make_job(self, step):
        inputobj = {}

        if "scatter" in step.tool:
            inputparms = copy.deepcopy(step.tool["inputs"])
            scatter = aslist(step.tool["scatter"])
            for i in inputparms:
                if i["id"] in scatter:
                    i["type"] = {"type": "array", "items": i["type"]}
        else:
            inputparms = step.tool["inputs"]

        for i in inputparms:
            _logger.debug(i)
            if "connect" in i:
                connect = i["connect"]
                is_array = isinstance(i["type"], dict) and i["type"]["type"] == "array"

                for c in aslist(connect):
                    src = idk(c["source"])
                    if src in self.state:
                        if self.state[src].parameter["type"] == i["type"]:
                            # source and input types are the same
                            if is_array and idk(i["id"]) in inputobj:
                                # concatenate arrays
                                inputobj[idk(i["id"])].extend(self.state[src].value)
                            else:
                                # just assign the value from state to input
                                inputobj[idk(i["id"])] = copy.deepcopy(self.state[src].value)
                        elif is_array and self.state[src].parameter["type"] == i["type"]["items"]:
                            # source type is the item type on the input array
                            # promote single item to array entry
                            if idk(i["id"]) in inputobj:
                                inputobj[idk(i["id"])].append(self.state[src][1])
                            else:
                                inputobj[idk(i["id"])] = [self.state[src][1]]
                        else:
                            raise Exception("Type mismatch '%s' and '%s'" % (src, i["id"][1:]))
                    else:
                        return None
            elif "default" in i:
                inputobj[idk(i["id"])] = i["default"]
            else:
                raise Exception("Value for %s not specified" % (i["id"]))

        _logger.info("Creating job with input: %s", inputobj)
        if "scatter" in step.tool:
            if step.tool.get("scatterType") == "dotproduct" or step.tool.get("scatterType") is None:
                step = DotProductScatter(step, aslist(step.tool["scatter"]))
            elif step.tool.get("scatterType") == "nested_crossproduct":
                step = NestedCrossProductScatter(step, aslist(step.tool["scatter"]))
            elif step.tool.get("scatterType") == "flat_crossproduct":
                step = FlatCrossProductScatter(step, aslist(step.tool["scatter"]))
        return step.job(inputobj, self.basedir)

    def run(self, outdir=None, **kwargs):
        for s in self.steps:
            s.completed = False

        run_all = len(self.steps)
        while run_all:
            made_progress = False
            for s in self.steps:
                if not s.completed:
                    job = self.try_make_job(s)
                    if job:
                        (joutdir, output) = job.run(outdir=outdir, **kwargs)
                        for i in s.tool["outputs"]:
                            _logger.info("Job got output: %s", output)
                            if "id" in i:
                                if idk(i["id"]) in output:
                                    self.state[idk(i["id"])] = WorkflowStateItem(i, output[idk(i["id"])])
                                else:
                                    raise Exception("Output is missing expected field %s" % idk(i["id"]))
                        s.completed = True
                        made_progress = True
                        run_all -= 1
            if not made_progress:
                raise Exception("Deadlocked")

        wo = {}
        for i in self.outputs:
            if "connect" in i:
                src = idk(i["connect"]["source"])
                wo[idk(i["id"])] = self.state[src][1]

        return (outdir, wo)


class Workflow(Process):
    def __init__(self, toolpath_object):
        super(Workflow, self).__init__(toolpath_object, "Workflow")

    def job(self, joborder, basedir, use_container=True):
        wj = WorkflowJob()
        wj.basedir = basedir
        wj.steps = [makeTool(s, basedir) for s in self.tool.get("steps", [])]
        random.shuffle(wj.steps)

        wj.state = {}
        for i in self.tool["inputs"]:
            iid = idk(i["id"])
            if iid in joborder:
                wj.state[iid] = WorkflowStateItem(i, copy.deepcopy(joborder[iid]))
            elif "default" in i:
                wj.state[iid] = WorkflowStateItem(i, copy.deepcopy(i["default"]))
        wj.outputs = self.tool["outputs"]
        return wj

class ExternalJob(object):
    def __init__(self, tool, innerjob):
        self.tool = tool
        self.innerjob = innerjob

    def run(self, **kwargs):
        self.impl = self.tool["impl"]
        (outdir, output) = self.innerjob.run(**kwargs)
        for i in self.tool["outputs"]:
            d = i["def"][len(self.impl)+1:]
            output[idk(i["id"])] = output[d]
            del output[d]

        return (outdir, output)

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

    def job(self, joborder, basedir, **kwargs):
        for i in self.tool["inputs"]:
            d = i["def"][len(self.impl)+1:]
            joborder[d] = joborder[idk(i["id"])]
            del joborder[idk(i["id"])]

        return ExternalJob(self.tool, self.embedded_tool.job(joborder, basedir, **kwargs))

class ScatterJob(object):
    def __init__(self, outputports, jobs):
        self.outputports = outputports
        self.jobs = jobs

    def run(self, **kwargs):
        outputs = {}
        for outschema in self.outputports:
            outputs[idk(outschema["id"])] = []
        for j in self.jobs:
            (_, out) = j.run(**kwargs)
            for outschema in self.outputports:
                outputs[idk(outschema["id"])].append(out[idk(outschema["id"])])
        return (None, outputs)

class DotProductScatter(object):
    def __init__(self, process, scatter_keys):
        self.process = process
        self.scatter_keys = scatter_keys

        self.outputports = []
        for out in self.process.tool["outputs"]:
            newout = copy.deepcopy(out)
            newout["type"] = {"type": "array", "items": out["type"]}
            self.outputports.append(newout)
        self.tool = {"outputs": self.outputports}

    def job(self, joborder, basedir, **kwargs):
        jobs = []

        l = None
        for s in self.scatter_keys:
            if l is None:
                l = len(joborder[idk(s)])
            elif l != len(joborder[idk(s)]):
                raise Exception("Length of input arrays must be equal when performing dotproduct scatter.")

        for i in range(0, l):
            jo = copy.copy(joborder)
            for s in self.scatter_keys:
                jo[idk(s)] = joborder[idk(s)][i]
            jobs.append(self.process.job(jo, basedir, **kwargs))

        return ScatterJob(self.outputports, jobs)
