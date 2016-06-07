#!/usr/bin/env python

import os
import sys
import shutil

import setuptools.command.egg_info as egg_info_cmd

from setuptools import setup, find_packages

SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, 'README.rst')

try:
    import gittaggers
    tagger = gittaggers.EggInfoFromGit
except ImportError:
    tagger = egg_info_cmd.egg_info

if os.path.exists("requirements.txt"):
    requirements = [
        r for r in open("requirements.txt").read().split("\n") if ";" not in r]
else:
    # In tox, it will cover them anyway.
    requirements = []

install_requires = [
    'requests',
    'ruamel.yaml',
    'rdflib >= 4.1.0',
    'rdflib-jsonld >= 0.3.0',
    'mistune',
    'typing']

install_requires.append("avro")  # TODO: remove me once cwltool is
# available in Debian Stable, Ubuntu 12.04 LTS

# extras_require={                # TODO: uncomment me, same conditions as above
#        ':python_version<"3"': ['avro'],
#        ':python_version>="3"': ['avro-python3']}
extras_require = {}               # TODO: to be removed when the above is added

setup(name='schema-salad',
      version='1.11',
      description='Schema Annotations for Linked Avro Data (SALAD)',
      long_description=open(README).read(),
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/common-workflow-language/common-workflow-language",
      download_url="https://github.com/common-workflow-language/common-workflow-language",
      license='Apache 2.0',
      packages=["schema_salad"],
      package_data={'schema_salad': ['metaschema/*']},
      install_requires=install_requires,
      extras_require=extras_require,
      test_suite='tests',
      tests_require=[],
      entry_points={
          'console_scripts': ["schema-salad-tool=schema_salad.main:main"]
      },
      zip_safe=True,
      cmdclass={'egg_info': tagger},
      classifiers=[
          "Environment :: Console",
          "Intended Audience :: Science/Research",
          "Operating System :: POSIX :: Linux",
          "Operating System :: MacOS :: MacOS X",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python :: 2.7",
          #"Programming Language :: Python :: 3.3",  # TODO: uncomment these
          #"Programming Language :: Python :: 3.4",  # lines
          #"Programming Language :: Python :: 3.5"
      ]
      )
