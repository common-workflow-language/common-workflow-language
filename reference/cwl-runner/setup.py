#!/usr/bin/env python

import os
import sys
import setuptools.command.egg_info as egg_info_cmd
import shutil

from setuptools import setup, find_packages

SETUP_DIR = os.path.dirname(__file__)



setup(name='cwl_runner',
      version='1.0',
      description='Common workflow language reference implementation',
      long_description="""This provides an alternate entry point to 'cwltool' allowing 'cwl-runner' to be used as an implementation-agnostic script interpreter via #!/usr/bin/env cwl-runner.""",
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/common-workflow-language/common-workflow-language",
      download_url="https://github.com/common-workflow-language/common-workflow-language",
      license='Apache 2.0',
      install_requires=[
          'cwltool'
        ],
      entry_points={
          'console_scripts': [ "cwl-runner=cwltool.main:main" ]
      },
      zip_safe=True
)
