import os
import random

class PathMapper(object):
    # Maps files to their absolute path
    def __init__(self, referenced_files, basedir):
        self._pathmap = {}
        for src in referenced_files:
            ab = src if os.path.isabs(src) else os.path.join(basedir, src)
            self._pathmap[src] = ab

    def mapper(self, src):
        return self._pathmap[src]


class DockerPathMapper(object):
    def __init__(self, referenced_files, basedir):
        self._pathmap = {}
        self.dirs = {}
        for src in referenced_files:
            abs = src if os.path.isabs(src) else os.path.abspath(os.path.join(basedir, src))
            dir, fn = os.path.split(abs)

            subdir = False
            for d in self.dirs:
                if dir.startswith(d):
                  subdir = True
                  break

            if not subdir:
                for d in list(self.dirs):
                    if d.startswith(dir):
                        # 'dir' is a parent of 'd'
                        del self.dirs[d]
                self.dirs[dir] = True

        prefix = "job" + str(random.randint(1, 1000000000)) + "_"

        names = set()
        for d in self.dirs:
            name = os.path.join("/tmp", prefix + os.path.basename(d))
            i = 1
            while name in names:
                i += 1
                name = os.path.join("/tmp", prefix + os.path.basename(d) + str(i))
            names.add(name)
            self.dirs[d] = name

        for src in referenced_files:
            abs = src if os.path.isabs(src) else os.path.abspath(os.path.join(basedir, src))
            for d in self.dirs:
                if abs.startswith(d):
                    self._pathmap[src] = os.path.join(self.dirs[d], abs[len(d)+1:])

    def mapper(self, src):
        return self._pathmap[src]
