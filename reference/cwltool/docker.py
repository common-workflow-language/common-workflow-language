import subprocess
import logging
import sys
import requests
import os

_logger = logging.getLogger("cwltool")

def get_image(dockerRequirement, pull_image, dry_run=False):
    found = False

    if "dockerImageId" not in dockerRequirement and "dockerPull" in dockerRequirement:
        dockerRequirement["dockerImageId"] = dockerRequirement["dockerPull"]

    for ln in subprocess.check_output(["docker", "images", "--no-trunc", "--all"]).splitlines():
        try:
            ln.index(dockerRequirement["dockerImageId"])
            found = True
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
                    raise Exception("Docker load returned non-zero exit status %i" % (rcode))
                found = True

    return found


def get_from_requirements(requirements, hints, pull_image, dry_run=False):
    if requirements:
        for r in reversed(requirements):
            if r["class"] == "DockerRequirement":
                if get_image(r, pull_image, dry_run):
                    return r["dockerImageId"]
                else:
                    raise Exception("Docker image %s not found" % (self.container["imageId"]))
    if hints:
        for r in reversed(hints):
            if r["class"] == "DockerRequirement":
                if get_image(r, pull_image, dry_run):
                    return r["dockerImageId"]

    return None
