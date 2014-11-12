import subprocess

class Job(object):
    def remap_files():
        pass

    def run(self):
        runtime = []

        print self.pathmap

        if self.container:
            runtime = ["docker", "run", self.container["imageId"]]

        stdin = None
        stdout = None

        sp = subprocess.Popen(runtime + self.command_line, shell=False, stdin=stdin, stdout=stdout)

        sp.wait()
