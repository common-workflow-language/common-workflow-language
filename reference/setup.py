#!/usr/bin/env python

import os
import sys
import setuptools.command.egg_info as egg_info_cmd
import shutil

from setuptools import setup, find_packages

SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, 'README.rst')

try:
    import gittaggers
    tagger = gittaggers.EggInfoFromGit
except ImportError:
    tagger = egg_info_cmd.egg_info

# Remove the symlink and copy the schemas directory.
# This is a total hack, but older versions of setuptools
# won't follow symlinks or follow relative paths outside the
# source directory (ugh!)
restore = False
if os.path.islink("cwltool/schemas") and os.path.exists("../schemas"):
    os.unlink("cwltool/schemas")
    shutil.copytree("../schemas", "cwltool/schemas")
    restore = True

setup(name='cwltool',
      version='1.0',
      description='Common workflow language reference implementation',
      long_description=open(README).read(),
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/common-workflow-language/common-workflow-language",
      download_url="https://github.com/common-workflow-language/common-workflow-language",
      license='Apache 2.0',
      packages=["cwltool", "cwltool.avro_ld"],
      package_data={'cwltool': ['schemas/draft-1/*', 'schemas/draft-2/*']},
      install_requires=[
          'requests',
          'PyYAML',
          'avro',
          'rdflib >= 4.2.0',
          'rdflib-jsonld >= 0.3.0',
          'mistune'
        ],
      test_suite='tests',
      tests_require=[],
      entry_points={
          'console_scripts': [ "cwltool=cwltool.main:main" ]
      },
      zip_safe=False,
      cmdclass={'egg_info': tagger},
)

if restore:
    # Restore the symlink
    shutil.rmtree("cwltool/schemas")
    os.symlink("../../schemas", "cwltool/schemas")
