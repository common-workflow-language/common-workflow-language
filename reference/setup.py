from setuptools import setup

setup(name='cwltool',
      version='1.0',
      description='Common workflow language reference implementation',
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/curoverse/common-workflow-language",
      download_url="https://github.com/curoverse/common-workflow-language",
      license='Apache 2.0',
      packages=["cwltool"],
      package_data={'cwltool': ['schemas/*.json']},
      include_package_data=True,
      scripts=[
        ],
      install_requires=[
          'jsonschema',
          'pyexecjs'
        ],
      test_suite='tests',
      tests_require=[],
      entry_points={
          'console_scripts': [ "cwltool=cwltool.main:main" ]
      }
)
