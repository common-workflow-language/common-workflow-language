import docker
import subprocess
import json
from aslist import aslist
import logging
import os
from process import WorkflowException
import process
import yaml
import validate

_logger = logging.getLogger("cwltool")

def exeval(ex, jobinput, requirements, docpath, context, pull_image):
    for r in reversed(requirements):
        if r["class"] == "ExpressionEngineRequirement" and r["id"] == ex["engine"]:
            if r["id"][0] != "#":
                with open(os.path.join(docpath, r["id"])) as f:
                    ex_obj = yaml.load(f)
                sch = process.get_schema()
                validate.validate_ex(sch.get_name("ExpressionEngineRequirement", ""), ex_obj)
                r = ex_obj

            runtime = []
            img_id = docker.get_from_requirements(r.get("requirements"), r.get("hints"), pull_image)
            if img_id:
                runtime = ["docker", "run", "-i", "--rm", img_id]

            exdefs = []
            for exdef in r.get("expressionDefs", []):
                if isinstance(exdef, dict) and "ref" in exdef:
                    with open(os.path.join(r["_docpath"], exdef["ref"])) as f:
                        exdefs.append(f.read())
                elif isinstance(exdef, basestring):
                    exdefs.append(exdef)

            inp = {
                "script": ex["script"],
                "expressionDefs": exdefs,
                "job": jobinput,
                "context": context
            }

            _logger.debug(json.dumps(inp))

            sp = subprocess.Popen(runtime + aslist(r["engineCommand"]),
                             shell=False,
                             close_fds=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)

            (stdoutdata, stderrdata) = sp.communicate(json.dumps(inp) + "\n\n")
            if sp.returncode != 0:
                raise WorkflowException("Expression engine returned non-zero exit code.")

            return json.loads(stdoutdata)

    raise WorkflowException("Unknown expression engine '%s'" % ex["engine"])

def do_eval(ex, jobinput, requirements, docpath, context=None, pull_image=True):
    if isinstance(ex, dict) and "engine" in ex and "script" in ex:
        return exeval(ex, jobinput, requirements, docpath, context, pull_image)
    else:
        return ex
