import subprocess
import logging
import sys
import requests
import os
import process
import re
import tempfile

_logger = logging.getLogger("cwltool")

def get_image(dockerRequirement, pull_image, dry_run=False):
    found = False

    if "dockerImageId" not in dockerRequirement and "dockerPull" in dockerRequirement:
        dockerRequirement["dockerImageId"] = dockerRequirement["dockerPull"]

    for ln in subprocess.check_output(["docker", "images", "--no-trunc", "--all"]).splitlines():
        try:
            m = re.match(r"^([^ ]+)\s+([^ ]+)\s+([^ ]+)", ln)
            sp = dockerRequirement["dockerImageId"].split(":")
            if len(sp) == 1:
                sp.append("latest")
            # check for repository:tag match or image id match
            if ((sp[0] == m.group(1) and sp[1] == m.group(2)) or dockerRequirement["dockerImageId"] == m.group(3)):
                found = True
                break
        except ValueError:
            pass

    if not found and pull_image:
        if "dockerPull" in dockerRequirement:
            cmd = ["docker", "pull", dockerRequirement["dockerPull"]]
            _logger.info(str(cmd))
            if not dry_run:
                subprocess.check_call(cmd, stdout=sys.stderr)
                found = True
        elif "dockerFile" in dockerRequirement:
            dockerfile_dir = tempfile.mkdtemp()
            with open(os.path.join(dockerfile_dir, "Dockerfile"), "w") as df:
                df.write(dockerRequirement["dockerFile"])
            cmd = ["docker", "build", "--tag=%s" % dockerRequirement["dockerImageId"], dockerfile_dir]
            _logger.info(str(cmd))
            if not dry_run:
                subprocess.check_call(cmd, stdout=sys.stderr)
                found = True
        elif "dockerLoad" in dockerRequirement:
            cmd = ["docker", "load"]
            _logger.info(str(cmd))
            if not dry_run:
                if os.path.exists(dockerRequirement["dockerLoad"]):
                    _logger.info("Loading docker image from %s", dockerRequirement["dockerLoad"])
                    with open(dockerRequirement["dockerLoad"], "rb") as f:
                        loadproc = subprocess.Popen(cmd, stdin=f, stdout=sys.stderr)
                else:
                    loadproc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=sys.stderr)
                    _logger.info("Sending GET request to %s", dockerRequirement["dockerLoad"])
                    req = requests.get(dockerRequirement["dockerLoad"], stream=True)
                    n = 0
                    for chunk in req.iter_content(1024*1024):
                        n += len(chunk)
                        _logger.info(str(n))
                        loadproc.stdin.write(chunk)
                    loadproc.stdin.close()
                rcode = loadproc.wait()
                if rcode != 0:
                    raise process.WorkflowException("Docker load returned non-zero exit status %i" % (rcode))
                found = True
        elif "dockerImport" in dockerRequirement:
            cmd = ["docker", "import", dockerRequirement["dockerImport"], dockerRequirement["dockerImageId"]]
            _logger.info(str(cmd))
            if not dry_run:
                subprocess.check_call(cmd, stdout=sys.stderr)

    return found


def get_from_requirements(r, req, pull_image, dry_run=False):
    if r:
        errmsg = None
        try:
            subprocess.check_output(["docker", "version"])
        except subprocess.CalledProcessError as e:
            errmsg = "Cannot communicate with docker daemon: " + str(e)
        except OSError as e:
            errmsg = "'docker' executable not found: " + str(e)

        if errmsg:
            if req:
                raise process.WorkflowException(errmsg)
            else:
                return None

        if get_image(r, pull_image, dry_run):
            return r["dockerImageId"]
        else:
            if req:
                raise process.WorkflowException("Docker image %s not found" % r["dockerImageId"])

    return None
