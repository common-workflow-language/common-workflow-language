Common Workflow Language
========================

This repo holds in-development draft description of the specification being developed on the
[Common Workflow Language mailing list](https://groups.google.com/forum/#!forum/common-workflow-language).

The Common Workflow Language (CWL) is an informal, multi-vendor working group
consisting of various organizations and individuals that have an interest in
portability of data analysis workflows.  Our goal is to create specifications
that enable data scientists to describe analysis tools and workflows that are
powerful, easy to use, portable, and support reproducibility.

CWL builds on technologies such as [JSON-LD](http://json-ld.org) and
[Avro](https://avro.apache.org/) for data modeling and
[Docker](http://docker.com) for portable runtime environments.

CWL can be used to describe workflows for a variety of areas such as:

* Data-intensive science, such as Bioinformatics, Chemistry, Physics, Astronomy
* Log analysis
* Data mining
* Extract, Transform and Load (ETL)
* Photo and video processing

Please be aware that Common Workflow Language is still under heavy development.
The current draft is draft 2.

## Repository contents

[Draft specifications](specification/)

[Schemas](schemas/)

[Conformance test suite](conformance/)

[Reference implementation](reference/)

[Examples](examples/)

## Implementations

Current implementations of the common workflow language tool description:

* [Reference implementation (Python)](reference/)
* [Rabix (Python)](https://github.com/rabix/rabix)
* [Cliche (Javascript)](https://github.com/rabix/cliche)

## Contributing

If you are interested in contributing ideas or code, please join the
[mailing list](https://groups.google.com/forum/#!forum/common-workflow-language) or fork
the repository and send a pull request!
