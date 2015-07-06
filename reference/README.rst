==================================================================
Common workflow language tool description reference implementation
==================================================================

This is the reference implementation of the Common Workflow Language.  It is
intended to be feature complete and provide comprehensive validation of CWL
files as well as provide other tools related to working with CWL.

This is written and tested for Python 2.7.

The reference implementation consists of two packages.  The "cwltool" package
is the primary Python module containing the reference implementation in the
"cwltool" module and console executable by the same name.

The "cwl-runner" package is optional and provides an additional entry point
under the alias "cwl-runner", which is the implementation-agnostic name for the
default CWL interpreter installed on a host.

Install
-------

From source::

  git clone https://github.com/common-workflow-language/common-workflow-language.git
  cd common-workflow-language/reference && python setup.py install
  cd cwl-runner && python setup.py install

Or installing the official package from PyPi (it will install "cwltool" package as well)::

  pip install cwl-runner

Run on the command line
-----------------------

  ``cwl-runner [tool] [job]``

Import as a module
----------------

Add::

  import cwltool

to your script.
