import subprocess
import os
import tempfile
import glob
import json
import yaml
import logging
import sys

_logger = logging.getLogger("cwltool")

class CommandLineJob(object):
    def run(self, dry_run=False, pull_image=True, outdir=None):
        if not outdir:
            if not dry_run:
                outdir = tempfile.mkdtemp()
            else:
                outdir = "/tmp"

        with open(os.path.join(outdir, "job.cwl.json"), "w") as fp:
            json.dump(self.joborder, fp)

        runtime = []

        if self.container and self.container.get("type") == "docker":
            if pull_image:
                if "pull" in self.container:
                    cmd = ["docker", "pull", self.container["pull"]]
                    _logger.info(str(cmd))
                    if not dry_run:
                        subprocess.check_call(["docker", "pull", self.container["pull"]], stdout=sys.stderr)
                elif "import" in self.container:
                    cmd = ["docker", "import", self.container["import"]]
                    _logger.info(str(cmd))
                    if not dry_run:
                        subprocess.check_call(["docker", "import", self.container["import"]], stdout=sys.stderr)

            runtime = ["docker", "run", "-i"]
            for d in self.pathmapper.dirs:
                runtime.append("--volume=%s:%s:ro" % (os.path.abspath(d), self.pathmapper.dirs[d]))
            runtime.append("--volume=%s:%s:ro" % (os.path.abspath(outdir), "/tmp/job_output"))
            runtime.append("--workdir=%s" % ("/tmp/job_output"))
            runtime.append("--user=%s" % (os.geteuid()))
            runtime.append(self.container["imageId"])

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

        sp = subprocess.Popen(runtime + self.command_line, shell=False, stdin=stdin, stdout=stdout)

        if stdin == subprocess.PIPE:
            sp.stdin.close()

        sp.wait()

        if stdin != subprocess.PIPE:
            stdin.close()

        if stdout:
            stdout.close()

        return (outdir, self.collect_outputs(outdir))
