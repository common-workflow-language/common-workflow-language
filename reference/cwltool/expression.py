import docker
import subprocess
import json
from aslist import aslist
import logging
import os
from process import WorkflowException, get_feature
import process
import yaml
import avro_ld.validate as validate
import avro_ld.ref_resolver

_logger = logging.getLogger("cwltool")

def exeval(ex, jobinput, requirements, docpath, context, pull_image):
    if ex["engine"] == "cwl:JsonPointer":
        try:
            obj = {"job": jobinput, "context": context}
            return avro_ld.ref_resolver.resolve_json_pointer(obj, ex["script"])
        except ValueError as v:
            raise WorkflowException("%s in %s" % (v,  obj))

    for r in reversed(requirements):
        if r["class"] == "ExpressionEngineRequirement" and r["id"] == ex["engine"]:
            runtime = []

            (docker_req, docker_is_req) = process.get_feature("DockerRequirement", requirements=r.get("requirements"), hints=r.get("hints"))
            if docker_req:
                img_id = docker.get_from_requirements(docker_req, docker_is_req, pull_image)
            if img_id:
                runtime = ["docker", "run", "-i", "--rm", img_id]

            exdefs = []
            for exdef in r.get("expressionDefs", []):
                if isinstance(exdef, dict) and "ref" in exdef:
                    with open(exdef["ref"][7:]) as f:
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
