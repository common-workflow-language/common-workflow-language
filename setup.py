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

setup(name='schema-salad',
      version='1.0.4',
      description='Schema Annotations for Linked Avro Data (SALAD)',
      long_description=open(README).read(),
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/common-workflow-language/common-workflow-language",
      download_url="https://github.com/common-workflow-language/common-workflow-language",
      license='Apache 2.0',
      packages=["schema_salad"],
      package_data={'schema_salad': ['metaschema.yml']},
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
          'console_scripts': [ "schema-salad-tool=schema_salad.main:main" ]
      },
      zip_safe=True,
      cmdclass={'egg_info': tagger},
)
