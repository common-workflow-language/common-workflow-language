import subprocess
import os
import tempfile
import glob
import json
import yaml

class Job(object):
    def run(self, dry_run=False, pull_image=True):
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
                    subprocess.call(["docker", "pull", self.container["pull"]])
                elif "import" in self.container:
                    subprocess.call(["docker", "import", self.container["import"]])

            runtime = ["docker", "run", "-i"]
            for d in self.pathmapper.dirs:
                runtime.append("--volume=%s:%s:ro" % (os.path.abspath(d), self.pathmapper.dirs[d]))
            runtime.append("--volume=%s:%s:ro" % (outdir, "/tmp/job_output"))
            runtime.append("--workdir=%s" % ("/tmp/job_output"))
            runtime.append("--user=%s" % (os.geteuid()))
            runtime.append(self.container["imageId"])

        stdin = None
        stdout = None

        print runtime + self.command_line

        if not dry_run:
            if self.stdin:
                stdin = open(self.stdin, "rb")

            os.chdir(outdir)

            if self.stdout:
                stdout = open(self.stdout, "wb")

            for t in self.generatefiles:
                with open(os.path.join(outdir, t), "w") as f:
                    f.write(self.generatefiles[t])

            sp = subprocess.Popen(runtime + self.command_line, shell=False, stdin=stdin, stdout=stdout)
            sp.wait()

            if stdin:
                stdin.close()

            if stdout:
                stdout.close()

            print "Output directory is %s" % outdir

            result_path = os.path.join(outdir, "result.cwl.json")
            if os.path.isfile(result_path):
                print "Result file found."
                with open(result_path) as fp:
                    return yaml.load(fp)
            else:
                return self.collect_outputs(outdir)

        return None
