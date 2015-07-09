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
import stat

_logger = logging.getLogger("cwltool")

def deref_links(outputs):
    if isinstance(outputs, dict):
        if outputs.get("class") == "File":
            st = os.lstat(outputs["path"])
            if stat.S_ISLNK(st.st_mode):
                outputs["path"] = os.readlink(outputs["path"])
        else:
            for v in outputs.values():
                deref_links(v)
    if isinstance(outputs, list):
        for v in outputs:
            deref_links(v)

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
            env = os.environ
            img_id = docker.get_from_requirements(docker_req, docker_is_req, pull_image)
            runtime = ["docker", "run", "-i"]
            for src in self.pathmapper.files():
                vol = self.pathmapper.mapper(src)
                runtime.append("--volume=%s:%s:ro" % vol)
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

        _logger.info("outdir is %s", self.outdir)
        _logger.info("%s%s%s",
                     " ".join(runtime + self.command_line),
                     ' < %s' % (self.stdin) if self.stdin else '',
                     ' > %s' % os.path.join(self.outdir, self.stdout) if self.stdout else '')

        if dry_run:
            return (self.outdir, {})

        outputs = {}

        try:
            for t in self.generatefiles:
                if isinstance(self.generatefiles[t], dict):
                    os.symlink(self.generatefiles[t]["path"], os.path.join(self.outdir, t))
                else:
                    with open(os.path.join(self.outdir, t), "w") as f:
                        f.write(self.generatefiles[t])

            if self.stdin:
                stdin = open(self.pathmapper.mapper(self.stdin)[0], "rb")
            else:
                stdin = subprocess.PIPE

            if self.stdout:
                absout = os.path.join(self.outdir, self.stdout)
                dn = os.path.dirname(absout)
                if dn and not os.path.exists(dn):
                    os.makedirs(dn)
                stdout = open(absout, "wb")
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

            for t in self.generatefiles:
                if isinstance(self.generatefiles[t], dict):
                    os.remove(os.path.join(self.outdir, t))
                    os.symlink(self.pathmapper.reversemap(self.generatefiles[t]["path"])[1], os.path.join(self.outdir, t))

            outputs = self.collect_outputs(self.outdir)

        except Exception as e:
            _logger.exception("Exception while running job")
            processStatus = "permanentFail"

        self.output_callback(outputs, processStatus)

        if rm_tmpdir:
            _logger.info("Removing temporary directory %s", self.tmpdir)
            shutil.rmtree(self.tmpdir, True)
