import docker
import subprocess
import json
from aslist import aslist
import logging
import os
from errors import WorkflowException
import process
import yaml
import schema_salad.validate as validate
import schema_salad.ref_resolver

_logger = logging.getLogger("cwltool")

def exeval(ex, jobinput, requirements, outdir, tmpdir, context, pull_image):
    if ex["engine"] == "https://w3id.org/cwl/cwl#JsonPointer":
        try:
            obj = {"job": jobinput, "context": context, "outdir": outdir, "tmpdir": tmpdir}
            return schema_salad.ref_resolver.resolve_json_pointer(obj, ex["script"])
        except ValueError as v:
            raise WorkflowException("%s in %s" % (v,  obj))

    for r in reversed(requirements):
        if r["class"] == "ExpressionEngineRequirement" and r["id"] == ex["engine"]:
            runtime = []

            class DR(object):
                pass
            dr = DR()
            dr.requirements = r.get("requirements", [])
            dr.hints = r.get("hints", [])

            (docker_req, docker_is_req) = process.get_feature(dr, "DockerRequirement")
            img_id = None
            if docker_req:
                img_id = docker.get_from_requirements(docker_req, docker_is_req, pull_image)
            if img_id:
                runtime = ["docker", "run", "-i", "--rm", img_id]

            exdefs = []
            for exdef in r.get("engineConfig", []):
                if isinstance(exdef, dict) and "ref" in exdef:
                    with open(exdef["ref"][7:]) as f:
                        exdefs.append(f.read())
                elif isinstance(exdef, basestring):
                    exdefs.append(exdef)

            inp = {
                "script": ex["script"],
                "engineConfig": exdefs,
                "job": jobinput,
                "context": context,
                "outdir": outdir,
                "tmpdir": tmpdir,
            }

            _logger.debug("Invoking expression engine %s with %s",
                          runtime + aslist(r["engineCommand"]),
                                           json.dumps(inp, indent=4))

            sp = subprocess.Popen(runtime + aslist(r["engineCommand"]),
                             shell=False,
                             close_fds=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)

            (stdoutdata, stderrdata) = sp.communicate(json.dumps(inp) + "\n\n")
            if sp.returncode != 0:
                raise WorkflowException("Expression engine returned non-zero exit code on evaluation of\n%s" % json.dumps(inp, indent=4))

            return json.loads(stdoutdata)

    raise WorkflowException("Unknown expression engine '%s'" % ex["engine"])

def do_eval(ex, jobinput, requirements, outdir, tmpdir, context=None, pull_image=True):
    if isinstance(ex, dict) and "engine" in ex and "script" in ex:
        return exeval(ex, jobinput, requirements, outdir, tmpdir, context, pull_image)
    else:
        return ex
