import job
import draft1tool
import draft2tool
from process import Process
import copy
import logging
import random

_logger = logging.getLogger("cwltool")

def makeTool(toolpath_object):
    if "schema" in toolpath_object:
        return draft1tool.Tool(toolpath_object)
    elif toolpath_object["class"] == "CommandLineTool":
        return draft2tool.CommandLineTool(toolpath_object)
    elif toolpath_object["class"] == "ExpressionTool":
        return draft2tool.ExpressionTool(toolpath_object)
    elif toolpath_object["class"] == "Workflow":
        return Workflow(toolpath_object)
    elif "impl" in toolpath_object:
        return Step(toolpath_object)


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
                                self.state[i["id"][1:]] = output[i["id"][1:]]
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

class Step(Process):
    def job(self, joborder, basedir, use_container=True):
        # load the impl and instantiate that.
        pass
