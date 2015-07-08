Common Workflow Language
========================

The Common Workflow Language (CWL) is an informal, multi-vendor working group
consisting of various organizations and individuals that have an interest in
portability of data analysis workflows.  Our goal is to create specifications
that enable data scientists to describe analysis tools and workflows that are
powerful, easy to use, portable, and support reproducibility.

CWL builds on technologies such as [JSON-LD](http://json-ld.org) and
[Avro](https://avro.apache.org/) for data modeling and
[Docker](http://docker.com) for portable runtime environments.

CWL is designed to express workflows for data-intensive science, such as
Bioinformatics, Chemistry, Physics, and Astronomy.

## Current specification

The current stable specification is draft 2:

http://common-workflow-language.github.io/draft-2/

## Implementations

Implementations capable of running the Common Workflow Language:

* [Reference implementation (Python)](https://github.com/common-workflow-language/common-workflow-language/tree/master/reference/)
* [Rabix](https://github.com/rabix/rabix)
* [Arvados](https://arvados.org)

## Examples

[Github repository of example workflows.](https://github.com/common-workflow-language/workflows)

## Development and testing

The CWL effort is on Github:

https://github.com/common-workflow-language/common-workflow-language

There is a Jenkins server maintained by Curoverse that runs tests for the
reference implementation, builds and uploads packages, and builds and uploads
Docker images:

https://ci.curoverse.com/job/common-workflow-language/

Current build status: [![Build Status](https://ci.curoverse.com/buildStatus/icon?job=common-workflow-language)](https://ci.curoverse.com/job/common-workflow-language/)

## Contributing

If you are interested in contributing ideas or code, please join the [mailing
list](https://groups.google.com/forum/#!forum/common-workflow-language) or
[fork the repository](https://github.com/common-workflow-language/common-workflow-language)
and send a pull request!

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
* Michael R. Crusoe <mcrusoe@msu.edu>
* John Kern <kern3020@gmail.com>
* Hervé Ménager <herve.menager@gmail.com>
* Maxim Mikheev <mikhmv@biodatomics.com>
* Tim Pierce <twp@unchi.org>
* Stian Soiland-Reyes <soiland-reyes@cs.manchester.ac.uk>
* Luka Stojanovic <luka.stojanovic@sbgenomics.com>
* Nebojsa Tijanic <nebojsa.tijanic@sbgenomics.com>
* Sinisa Ivkovic <sinisa.ivkovic@sbgenomics.com>
* Robin Andeer <robin.andeer@gmail.com>
* Roman Valls Guimerà <brainstorm@nopcode.org>
* Guillermo Carrasco Hernandez <guille.ch.88@gmail.com>
