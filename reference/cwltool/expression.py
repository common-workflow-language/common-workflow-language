import docker
import subprocess
import json

def exeval(ex, jobinput, requirements, context, pull_image):
    for r in reversed(requirements):
        if r["class"] == "ExpressionEngineRequirement" and r["id"] == ex["engine"]:
            runtime = []
            img_id = docker.get_from_requirements(r.get("requirements"), r.get("hints"), pull_image)
            if img_id:
                runtime = ["docker", "run", "-i", "--rm", img_id]

            sp = subprocess.Popen(runtime + aslist(r["engineCommand"]),
                             shell=False,
                             close_fds=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)

            inp = {
                "script": ex["script"],
                "expressionDefs": r.get("expressionDefs"),
                "job": jobinput,
                "context": context
            }

            (stdoutdata, stderrdata) = sp.communicate(json.dumps(inp))

    raise WorkflowException("Unknown expression engine '%s'" % ex["engine"])

def do_eval(self, ex, jobinput, requirements, context=None, pull_image=True):
    if isinstance(ex, dict) and "engine" in ex and "script" in ex:
        return exeval(ex, jobinput, requirements, context)
    else:
        return ex
