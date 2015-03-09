import job
import draft1tool
import draft2tool
from process import Process
import copy
import logging
import random
from ref_resolver import from_url

_logger = logging.getLogger("cwltool")

def makeTool(toolpath_object):
    if "schema" in toolpath_object:
        return draft1tool.Tool(toolpath_object)
    elif "impl" in toolpath_object and toolpath_object.get("class", "External") == "External":
        return External(toolpath_object)
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
    def try_make_job(self, s):
        jo = {}
        for i in s.tool["inputs"]:
            _logger.debug(i)
            if "connect" in i:
                src = i["connect"]["source"][1:]
                if self.state.get(src):
                    jo[i["id"][1:]] = self.state.get(src)
                else:
                    return None
        _logger.info("Creating job with input: %s", jo)
        return s.job(jo, self.basedir)

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
                        (joutdir, output) = job.run(outdir=outdir)
                        for i in s.tool["outputs"]:
                            _logger.info("Job got output: %s", output)
                            if "id" in i:
                                if i["id"][1:] in output:
                                    self.state[i["id"][1:]] = output[i["id"][1:]]
                                else:
                                    raise Exception("Output is missing expected field %s" % i["id"][1:])
                        s.completed = True
                        made_progress = True
                        run_all -= 1
            if not made_progress:
                raise Exception("Deadlocked")

        wo = {}
        for i in self.outputs:
            if "connect" in i:
                src = i["connect"]["source"][1:]
                wo[i["id"][1:]] = self.state[src]

        return (outdir, wo)


class Workflow(Process):
    def __init__(self, toolpath_object):
        super(Workflow, self).__init__(toolpath_object, "Workflow")

    def job(self, joborder, basedir, use_container=True):
        wj = WorkflowJob()
        wj.basedir = basedir
        wj.steps = [makeTool(s) for s in self.tool.get("steps", [])]
        random.shuffle(wj.steps)
        wj.state = copy.deepcopy(joborder)
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
            output[i["id"][1:]] = output[d]
            del output[d]

        return (outdir, output)

class External(Process):
    def __init__(self, toolpath_object):
        self.impl = toolpath_object["impl"]
        self.embedded_tool = makeTool(from_url(self.impl))

        if "id" in toolpath_object:
            self.id = toolpath_object["id"]
        else:
            self.id = "#step_" + str(random.randint(1, 1000000000))

        for i in toolpath_object["inputs"]:
            d = i["def"][len(self.impl):]
            toolid = i.get("id", self.id + "." + d[1:])
            for a in self.embedded_tool.tool["inputs"]:
                if a["id"] == d:
                    i.update(a)
            i["id"] = toolid

        for i in toolpath_object["outputs"]:
            d = i["def"][len(self.impl):]
            toolid = i["id"]
            for a in self.embedded_tool.tool["outputs"]:
                if a["id"] == d:
                    i.update(a)
            i["id"] = toolid

        super(External, self).__init__(toolpath_object, "Process")

    def job(self, joborder, basedir, **kwargs):
        for i in self.tool["inputs"]:
            d = i["def"][len(self.impl)+1:]
            joborder[d] = joborder[i["id"][1:]]
            del joborder[i["id"][1:]]

        return ExternalJob(self.tool, self.embedded_tool.job(joborder, basedir, **kwargs))
