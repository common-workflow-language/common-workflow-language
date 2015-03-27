import subprocess
import os
import tempfile
import glob
import json
import yaml
import logging
import sys
import requests

_logger = logging.getLogger("cwltool")

class CommandLineJob(object):
    def run(self, dry_run=False, pull_image=True, outdir=None, rm_container=True):
        if not outdir:
            if not dry_run:
                outdir = tempfile.mkdtemp()
            else:
                outdir = "/tmp"

        with open(os.path.join(outdir, "job.cwl.json"), "w") as fp:
            json.dump(self.joborder, fp)

        runtime = []
        env = {}

        if self.container and self.container.get("type") == "docker":
            found = False
            for ln in subprocess.check_output(["docker", "images", "--no-trunc", "--all"]).splitlines():
                try:
                    ln.index(self.container["imageId"])
                    found = True
                except ValueError:
                    pass

            if not found and pull_image:
                if "file" in self.container:
                    dockerfile_dir = tempfile.mkdtemp()
                    with open(os.path.join(dockerfile_dir, "Dockerfile"), "w") as df:
                        df.write(self.container["file"])
                    cmd = ["docker", "build", "--tag=%s" % self.container["imageId"], dockerfile_dir]
                    _logger.info(str(cmd))
                    if not dry_run:
                        subprocess.check_call(cmd, stdout=sys.stderr)
                        found = True
                if "pull" in self.container:
                    cmd = ["docker", "pull", self.container["pull"]]
                    _logger.info(str(cmd))
                    if not dry_run:
                        subprocess.check_call(cmd, stdout=sys.stderr)
                        found = True
                elif "load" in self.container:
                    cmd = ["docker", "load"]
                    _logger.info(str(cmd))
                    if not dry_run:
                        if os.path.exists(self.container["load"]):
                            _logger.info("Loading docker image from %s", self.container["load"])
                            with open(self.container["load"], "rb") as f:
                                loadproc = subprocess.Popen(cmd, stdin=f, stdout=sys.stderr)
                        else:
                            _logger.info("Sending GET request to %s", self.container["load"])
                            req = requests.get(self.container["load"], stream=True)
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

            if found:
                runtime = ["docker", "run", "-i"]
                for d in self.pathmapper.dirs:
                    runtime.append("--volume=%s:%s:ro" % (os.path.abspath(d), self.pathmapper.dirs[d]))
                runtime.append("--volume=%s:%s:rw" % (os.path.abspath(outdir), "/tmp/job_output"))
                runtime.append("--workdir=%s" % ("/tmp/job_output"))
                runtime.append("--user=%s" % (os.geteuid()))
                if rm_container:
                    runtime.append("--rm")
                for t,v in self.environment.items():
                    runtime.append("--env=%s=%s" % (t, v))
                runtime.append(self.container["imageId"])
            else:
                raise Exception("Docker image %s not found" % (self.container["imageId"]))
        else:
            env = self.environment

        stdin = None
        stdout = None

        _logger.info("%s%s%s",
                     " ".join(runtime + self.command_line),
                     ' < %s' % (self.stdin) if self.stdin else '',
                     ' > %s' % (self.stdout) if self.stdout else '')

        if dry_run:
            return (outdir, {})

        if self.stdin:
            stdin = open(self.stdin, "rb")
        else:
            stdin = subprocess.PIPE

        os.chdir(outdir)

        if self.stdout:
            stdout = open(self.stdout, "wb")
        else:
            stdout = sys.stderr

        for t in self.generatefiles:
            with open(os.path.join(outdir, t), "w") as f:
                f.write(self.generatefiles[t])

        sp = subprocess.Popen(runtime + self.command_line,
                              shell=False,
                              close_fds=True,
                              stdin=stdin,
                              stdout=stdout,
                              env=env,
                              cwd=outdir)

        if stdin == subprocess.PIPE:
            sp.stdin.close()

        sp.wait()

        if stdin != subprocess.PIPE:
            stdin.close()

        if stdout != sys.stderr:
            stdout.close()

        return (outdir, self.collect_outputs(outdir))
