from setuptools import setup, find_packages

setup(name='cwllib',
      version='1.0',
      description='Common workflow language reference implementation',
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/curoverse/common-workflow-language",
      download_url="https://github.com/curoverse/common-workflow-language",
      license='Apache 2.0',
      packages=find_packages(),
      scripts=[
        ],
      install_requires=[
          'jsonschema',
          'pyexecjs'
        ],
      test_suite='tests',
      tests_require=[],
      zip_safe=False
      )
