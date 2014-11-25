#!/usr/bin/env python

import os
import subprocess
import time

from setuptools import setup, find_packages

SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, 'README.rst')

cmd_opts = {'egg_info': {}}
try:
    git_tags = subprocess.check_output(
        ['git', 'log', '--first-parent', '--max-count=1',
         '--format=format:%ct %h', SETUP_DIR]).split()
    assert len(git_tags) == 2
except (AssertionError, OSError, subprocess.CalledProcessError):
    pass
else:
    git_tags[0] = time.strftime('%Y%m%d%H%M%S', time.gmtime(int(git_tags[0])))
    cmd_opts['egg_info']['tag_build'] = '.{}.{}'.format(*git_tags)


setup(name='cwltool',
      version='0.1',
      description='Common workflow language reference implementation',
      long_description=open(README).read(),
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/rabix/common-workflow-language",
      download_url="https://github.com/rabix/common-workflow-language",
      license='Apache 2.0',
      packages=["cwltool"],
      package_data={'cwltool': ['schemas/*.json']},
      include_package_data=True,
      install_requires=[
          'jsonschema >= 2.4.0'
        ],
      test_suite='tests',
      tests_require=[],
      entry_points={
          'console_scripts': [ "cwltool=cwltool.main:main" ]
      },
      options=cmd_opts,
)
