import subprocess
import os

class Job(object):
    def remap_files():
        pass

    def run(self):
        runtime = []

        if self.container and self.container.get("type") == "docker":
            runtime = ["docker", "run"]
            for d in self.pathmapper.dirs:
                runtime.append("--volume=%s:%s:ro" % (d, self.pathmapper.dirs[d]))
            runtime.append(self.container["imageId"])

        stdin = None
        stdout = None

        print runtime + self.command_line

        sp = subprocess.Popen(runtime + self.command_line, shell=False, stdin=stdin, stdout=stdout)

        sp.wait()
