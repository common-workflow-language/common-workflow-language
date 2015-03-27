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

_logger = logging.getLogger("cwltool")

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


def should_fanout(src_type, dest_type):
    if isinstance(src_type, dict):
        if src_type["type"] == "array" and src_type["items"] == dest_type:
            return True
    return False

class WorkflowJob(object):
    def try_make_job(self, s):
        jo = {}
        fanout = None
        for i in s.tool["inputs"]:
            _logger.debug(i)
            if "connect" in i:
                connect = i["connect"]
                if isinstance(connect, list):
                    # Handle multiple inputs
                    if not fanout:
                        fanout = i["id"][1:]
                        jo[i["id"][1:]] = []
                    else:
                        raise Exception("Can only fanout on one port")
                for c in aslist(connect):
                    src = c["source"][1:]
                    if src in self.state:
                        if self.state[src][0]["type"] == i["type"]:
                            if fanout:
                                jo[i["id"][1:]].append(self.state[src][1])
                            else:
                                jo[i["id"][1:]] = self.state[src][1]
                        elif should_fanout(self.state[src][0]["type"], i["type"]):
                            if fanout:
                                if fanout == i["id"][1:]:
                                    jo[i["id"][1:]].extend(self.state[src][1])
                                else:
                                    raise Exception("Can only fanout on one port")
                            else:
                                fanout = i["id"][1:]
                                jo[i["id"][1:]] = self.state[src][1]
                        else:
                            raise Exception("Type mismatch '%s' and '%s'" % (src, i["id"][1:]))
                    else:
                        return None
            elif "default" in i:
                jo[i["id"][1:]] = i["default"]

        _logger.info("Creating job with input: %s", jo)
        if fanout:
            s = Fanout(s, fanout)
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
                        (joutdir, output) = job.run(outdir=outdir, **kwargs)
                        for i in s.tool["outputs"]:
                            _logger.info("Job got output: %s", output)
                            if "id" in i:
                                if i["id"][1:] in output:
                                    self.state[i["id"][1:]] = (i, output[i["id"][1:]])
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
                wo[i["id"][1:]] = self.state[src][1]

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
            iid = i["id"][1:]
            if iid in joborder:
                wj.state[iid] = (i, copy.deepcopy(joborder[iid]))
            elif "default" in i:
                wj.state[iid] = (i, copy.deepcopy(i["default"]))
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
    def __init__(self, toolpath_object, basedir):
        self.impl = toolpath_object["impl"]
        self.embedded_tool = makeTool(from_url(os.path.join(basedir, self.impl)), basedir)

        if "id" in toolpath_object:
            self.id = toolpath_object["id"]
        else:
            self.id = "#step_" + str(random.randint(1, 1000000000))

        for i in toolpath_object["inputs"]:
            d = i["def"][len(self.impl):]
            toolid = i.get("id", self.id + "." + d[1:])
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
            joborder[d] = joborder[i["id"][1:]]
            del joborder[i["id"][1:]]

        return ExternalJob(self.tool, self.embedded_tool.job(joborder, basedir, **kwargs))

class FanoutJob(object):
    def __init__(self, outputports, jobs):
        self.outputports = outputports
        self.jobs = jobs

    def run(self, **kwargs):
        outputs = {}
        for outschema in self.outputports:
            outputs[outschema["id"][1:]] = []
        for j in self.jobs:
            (_, out) = j.run(**kwargs)
            for outschema in self.outputports:
                outputs[outschema["id"][1:]].append(out[outschema["id"][1:]])
        return (None, outputs)

class Fanout(object):
    def __init__(self, process, fanout_key):
        self.process = process
        self.fanout_key = fanout_key
        self.outputports = []
        for out in self.process.tool["outputs"]:
            newout = copy.deepcopy(out)
            newout["type"] = {"type": "array", "items": out["type"]}
            self.outputports.append(newout)
        self.tool = {"outputs": self.outputports}

    def job(self, joborder, basedir, **kwargs):
        jobs = []
        for fn in joborder[self.fanout_key]:
            jo = copy.copy(joborder)
            jo[self.fanout_key] = fn
            jobs.append(self.process.job(jo, basedir, **kwargs))
        return FanoutJob(self.outputports, jobs)
