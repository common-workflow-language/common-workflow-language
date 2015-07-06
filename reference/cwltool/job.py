import subprocess
import os
import tempfile
import glob
import json
import yaml
import logging
import sys
import requests
import docker
from process import WorkflowException, get_feature
import shutil

_logger = logging.getLogger("cwltool")

class CommandLineJob(object):
    def run(self, dry_run=False, pull_image=True, rm_container=True, rm_tmpdir=True, **kwargs):

        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        #with open(os.path.join(outdir, "cwl.input.json"), "w") as fp:
        #    json.dump(self.joborder, fp)

        runtime = []
        env = {"TMPDIR": self.tmpdir}

        (docker_req, docker_is_req) = get_feature(self, "DockerRequirement")

        for f in self.pathmapper.files():
            if not os.path.exists(self.pathmapper.mapper(f)[0]):
                raise WorkflowException("Required input file %s not found" % self.pathmapper.mapper(f)[0])

        if docker_req and kwargs.get("use_container") is not False:
            img_id = docker.get_from_requirements(docker_req, docker_is_req, pull_image)
            runtime = ["docker", "run", "-i"]
            for d in self.pathmapper.dirs:
                runtime.append("--volume=%s:%s:ro" % (os.path.abspath(d), self.pathmapper.dirs[d]))
            runtime.append("--volume=%s:%s:rw" % (os.path.abspath(self.outdir), "/tmp/job_output"))
            runtime.append("--volume=%s:%s:rw" % (os.path.abspath(self.tmpdir), "/tmp/job_tmp"))
            runtime.append("--workdir=%s" % ("/tmp/job_output"))
            runtime.append("--user=%s" % (os.geteuid()))

            if rm_container:
                runtime.append("--rm")

            runtime.append("--env=TMPDIR=/tmp/job_tmp")

            for t,v in self.environment.items():
                runtime.append("--env=%s=%s" % (t, v))

            runtime.append(img_id)
        else:
            env = self.environment
            if not os.path.exists(self.tmpdir):
                os.makedirs(self.tmpdir)
            env["TMPDIR"] = self.tmpdir

        stdin = None
        stdout = None

        _logger.info("%s%s%s",
                     " ".join(runtime + self.command_line),
                     ' < %s' % (self.stdin) if self.stdin else '',
                     ' > %s' % (self.stdout) if self.stdout else '')

        if dry_run:
            return (self.outdir, {})

        os.chdir(self.outdir)

        for t in self.generatefiles:
            if isinstance(self.generatefiles[t], dict):
                os.symlink(self.generatefiles[t]["path"], os.path.join(self.outdir, t))
            else:
                with open(os.path.join(self.outdir, t), "w") as f:
                    f.write(self.generatefiles[t])

        if self.stdin:
            stdin = open(self.stdin, "rb")
        else:
            stdin = subprocess.PIPE

        if self.stdout:
            dn = os.path.dirname(self.stdout)
            if dn and not os.path.exists(dn):
                os.makedirs(dn)
            stdout = open(self.stdout, "wb")
        else:
            stdout = sys.stderr

        sp = subprocess.Popen(runtime + self.command_line,
                              shell=False,
                              close_fds=True,
                              stdin=stdin,
                              stdout=stdout,
                              env=env,
                              cwd=self.outdir)

        if stdin == subprocess.PIPE:
            sp.stdin.close()

        rcode = sp.wait()

        if stdin != subprocess.PIPE:
            stdin.close()

        if stdout is not sys.stderr:
            stdout.close()

        outputs = self.collect_outputs(self.outdir)

        if self.successCodes and rcode in self.successCodes:
            processStatus = "success"
        elif self.temporaryFailCodes and rcode in self.temporaryFailCodes:
            processStatus = "temporaryFail"
        elif self.permanentFailCodes and rcode in self.permanentFailCodes:
            processStatus = "permanentFail"
        elif rcode == 0:
            processStatus = "success"
        else:
            processStatus = "permanentFail"

        self.output_callback(outputs, processStatus)

        if rm_tmpdir:
            _logger.info("Removing temporary directory %s", self.tmpdir)
            shutil.rmtree(self.tmpdir, True)
