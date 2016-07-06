from setuptools.command.egg_info import egg_info
import subprocess
import time

class EggInfoFromGit(egg_info):
    """Tag the build with git commit timestamp.

    If a build tag has already been set (e.g., "egg_info -b", building
    from source package), leave it alone.
    """
    def git_timestamp_tag(self):
        gitinfo = subprocess.check_output(
            ['git', 'log', '--first-parent', '--max-count=1',
             '--format=format:%ct', '.']).strip()
        return time.strftime('.%Y%m%d%H%M%S', time.gmtime(int(gitinfo)))

    def tags(self):
        if self.tag_build is None:
            try:
                self.tag_build = self.git_timestamp_tag()
            except (subprocess.CalledProcessError, OSError):
                pass
        return egg_info.tags(self)
