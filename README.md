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

CWL is intended to express workflows for data-intensive science, such as
Bioinformatics, Chemistry, Physics, and Astronomy.

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

## Participating Organizations

* [Curoverse](http://curoverse.com)
* [Seven Bridges Genomics](http://sbgenomics.com)
* [Galaxy](http://galaxyproject.org/)
* [Institut Pasteur](http://www.pasteur.fr)
* [BioDatomics](http://www.biodatomics.com/)
* [Michigan State University](http://ged.msu.edu/)
* [Broad Institute](https://www.broadinstitute.org)

## Individual Contributors

* Peter Amstutz <peter.amstutz@curoverse.com>
* John Chilton <jmchilton@gmail.com>
* Michael Crusoe <michael.crusoe@gmail.com>
* John Kern <kern3020@gmail.com>
* Hervé Ménager <herve.menager@gmail.com>
* Maxim Mikheev <mikhmv@biodatomics.com>
* Tim Pierce <twp@unchi.org>
* Stian Soiland-Reyes <soiland-reyes@cs.manchester.ac.uk>
* Luka Stojanovic <luka.stojanovic@sbgenomics.com>
* Nebojsa Tijanic <nebojsa.tijanic@sbgenomics.com>
