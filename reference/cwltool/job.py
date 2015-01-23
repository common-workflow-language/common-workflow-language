import subprocess
import os
import tempfile
import tool
import glob
import json


class Job(object):
    def run(self, dry_run=False):
        if not dry_run:
            outdir = tempfile.mkdtemp()
        else:
            outdir = "/tmp"

        with open(os.path.join(outdir, "job.cwl.json"), "w") as fp:
            json.dump(self.joborder, fp)

        runtime = []

        if self.container and self.container.get("type") == "docker":
            if "uri" in self.container:
                subprocess.call("docker", "pull", self.container["uri"])
            runtime = ["docker", "run", "-i"]
            for d in self.pathmapper.dirs:
                runtime.append("--volume=%s:%s:ro" % (d, self.pathmapper.dirs[d]))
            runtime.append("--volume=%s:%s:ro" % (outdir, "/tmp/job_output"))
            runtime.append("--workdir=%s" % ("/tmp/job_output"))
            runtime.append("--user=%s" % (os.geteuid()))
            runtime.append(self.container["imageId"])
        else:
            os.chdir(outdir)

        stdin = None
        stdout = None

        print runtime + self.command_line

        if not dry_run:
            if self.stdin:
                stdin = open(self.stdin, "rb")

            if self.stdout:
                stdout = open(os.path.join(outdir, self.stdout), "wb")

            sp = subprocess.Popen(runtime + self.command_line, shell=False, stdin=stdin, stdout=stdout)
            sp.wait()

            if stdin:
                stdin.close()

            if stdout:
                stdout.close()

            print "Output directory is %s" % outdir
            return self.collect_outputs(self.tool.tool["outputs"], outdir)
        else:
            return None

    def collect_outputs(self, schema, outdir):
        result_path = os.path.join(outdir, "result.cwl.json")
        if os.path.isfile(result_path):
            print "Result file found."
            with open(result_path) as fp:
                return json.load(fp)

        r = None
        if isinstance(schema, dict):
            if "adapter" in schema:
                adapter = schema["adapter"]
                if "glob" in adapter:
                    r = [{"path": g} for g in glob.glob(os.path.join(outdir, adapter["glob"]))]
                    if not ("type" in schema and schema["type"] == "array"):
                        if r:
                            r = r[0]
                        else:
                            r = None
                if "value" in adapter:
                    r = tool.resolve_eval(self.joborder, adapter["value"])
            if not r and "properties" in schema:
                r = {}
                for k, v in schema["properties"].items():
                    out = self.collect_outputs(v, outdir)
                    if out:
                        r[k] = out

        return r
