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

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

if os.path.exists("requirements.txt"):
    requirements = [
        r for r in open("requirements.txt").read().split("\n") if ";" not in r]
else:
    # In tox, it will cover them anyway.
    requirements = []

install_requires = [
    'setuptools',
    'requests >= 1.0',
    'ruamel.yaml >= 0.12.4',
    'rdflib >= 4.2.0, < 4.3.0',
    'rdflib-jsonld >= 0.3.0, < 0.5.0',
    'mistune >= 0.7.3, < 0.8',
    'typing >= 3.5.2, < 3.6',
    'CacheControl >= 0.11.7, < 0.12',
    'lockfile >= 0.9',
    'pathlib2 >= 2.1.0']

install_requires.append("avro")  # TODO: remove me once cwltool is
# available in Debian Stable, Ubuntu 12.04 LTS

# extras_require={                # TODO: uncomment me, same conditions as above
#        ':python_version<"3"': ['avro'],
#        ':python_version>="3"': ['avro-python3']}
extras_require = {}               # TODO: to be removed when the above is added

setup(name='schema-salad',
      version='2.1',
      description='Schema Annotations for Linked Avro Data (SALAD)',
      long_description=open(README).read(),
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/common-workflow-language/common-workflow-language",
      download_url="https://github.com/common-workflow-language/common-workflow-language",
      license='Apache 2.0',
      setup_requires=[] + pytest_runner,
      packages=["schema_salad", "schema_salad.tests"],
      package_data={'schema_salad': ['metaschema/*']},
      include_package_data=True,
      install_requires=install_requires,
      extras_require=extras_require,
      test_suite='tests',
      tests_require=['pytest'],
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
