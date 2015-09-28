import os
import random
import logging
import stat

_logger = logging.getLogger("cwltool")

def abspath(src, basedir):
    if src.startswith("file://"):
        ab = src[7:]
    else:
        ab = src if os.path.isabs(src) else os.path.join(basedir, src)
    return ab

class PathMapper(object):
    """Mapping of files from relative path provided in the file to a tuple of
    (absolute local path, absolute container path)"""

    def __init__(self, referenced_files, basedir):
        self._pathmap = {}
        for src in referenced_files:
            ab = abspath(src, basedir)
            self._pathmap[src] = (ab, ab)

    def mapper(self, src):
        return self._pathmap[src]

    def files(self):
        return self._pathmap.keys()

    def reversemap(self, target):
        for k,v in self._pathmap.items():
            if v[1] == target:
                return (k, v[0])

class DockerPathMapper(PathMapper):
    def __init__(self, referenced_files, basedir):
        self._pathmap = {}
        self.dirs = {}
        for src in referenced_files:
            ab = abspath(src, basedir)
            dir, fn = os.path.split(ab)

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
            ab = abspath(src, basedir)

            deref = ab
            st = os.lstat(deref)
            while stat.S_ISLNK(st.st_mode):
                rl = os.readlink(deref)
                deref = rl if os.path.isabs(rl) else os.path.join(os.path.dirname(deref), rl)
                st = os.lstat(deref)

            for d in self.dirs:
                if ab.startswith(d):
                    self._pathmap[src] = (deref, os.path.join(self.dirs[d], ab[len(d)+1:]))
