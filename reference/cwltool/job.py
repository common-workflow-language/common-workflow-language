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

_logger = logging.getLogger("cwltool")

class CommandLineJob(object):
    def run(self, outdir, dry_run=False, pull_image=True, rm_container=True):

        with open(os.path.join(outdir, "cwl.input.json"), "w") as fp:
            json.dump(self.joborder, fp)

        runtime = []
        env = {}

        img_id = docker.get_from_requirements(self.requirements, self.hints, pull_image)

        if img_id:
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
            runtime.append(img_id)
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

        self.output_callback(self.collect_outputs(outdir))
