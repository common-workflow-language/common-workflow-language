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
Bioinformatics, Medical Imaging, Chemistry, Physics, and Astronomy.

## CWL Specification

The current stable specification is draft 2:

http://common-workflow-language.github.io/draft-2/

The current work in progress specification is draft 3:

http://common-workflow-language.github.io/draft-3/

## Implementations

Some of the software supporting running Common Workflow Language tools or workflows:

* [cwltool (reference implementation)](https://github.com/common-workflow-language/cwltool),
  [cwltool wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/cwltool-%28reference-implementation%29)
* [Rabix](https://github.com/rabix/rabix),
  [Rabix wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/Rabix)
* [Arvados](https://arvados.org),
  [Arvados wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/Arvados)
* [Galaxy](https://github.com/common-workflow-language/Galaxy),
  [Galaxy wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/Galaxy)
* [Parallel Recipes](https://github.com/yvdriess/precipes),
  [Parallel Recipes wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/Parallel-Recipes)
* [Toil](https://github.com/BD2KGenomics/toil),
  [Toil wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/Toil)
* [CancerCollaboratory](https://github.com/CancerCollaboratory),
  [CancerCollaboratory wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/CancerCollaboratory)
* [Airflow (SciDAP)](https://github.com/SciDAP/scidap),
  [Airflow wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/SciDAP)
* [cwl2script](https://github.com/common-workflow-language/cwl2script),
  [cwl2script page](https://github.com/common-workflow-language/common-workflow-language/wiki/cwl2script)

## Examples

[Github repository of example tools and workflows.](https://github.com/common-workflow-language/workflows)

## Development and testing

The CWL effort is on Github:

https://github.com/common-workflow-language/common-workflow-language

There is a Jenkins server maintained by Curoverse that runs tests for the
reference implementation, builds and uploads packages, and builds and uploads
Docker images:

https://ci.curoverse.com/job/common-workflow-language/

Current build status: [![Build Status](https://ci.curoverse.com/buildStatus/icon?job=common-workflow-language)](https://ci.curoverse.com/job/common-workflow-language/)

## Community and Contributing

If you are interested in learning more or contributing ideas or code,
[come chat with us on Gitter](https://gitter.im/common-workflow-language/common-workflow-language),
check out [#CommonWL on Twitter](https://twitter.com/search?q=%23CommonWL),
join the [mailing list common-workflow-language on Google Groups](https://groups.google.com/forum/#!forum/common-workflow-language) or
[fork the repository](https://github.com/common-workflow-language/common-workflow-language)
and send a pull request!

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/common-workflow-language/common-workflow-language?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Participating Organizations

* [Curoverse](http://curoverse.com)
* [Seven Bridges Genomics](http://sbgenomics.com)
* [Galaxy Project](http://galaxyproject.org/)
* [Apache Taverna](http://taverna.incubator.apache.org/)
* [Institut Pasteur](http://www.pasteur.fr)
* [Wellcome Trust Sanger Institute](https://www.sanger.ac.uk/)
* [University of California Davis](http://ucdavis.edu)
* [University of California Santa Cruz](https://cbse.soe.ucsc.edu/research/bioinfo)
* [Harvard Chan School of Public Health](http://www.hsph.harvard.edu/)
* [Cincinnati Children's Hospital Medical Center](http://www.cincinnatichildrens.org/)
* [Broad Institute](https://www.broadinstitute.org)
* [BioDatomics](http://www.biodatomics.com/)

## Individual Contributors

* Peter Amstutz <peter.amstutz@curoverse.com>
* John Chilton <jmchilton@gmail.com>
* Michael R. Crusoe <michael.crusoe@gmail.com>
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
* Brad Chapman <bchapman@hsph.harvard.edu>
* Josh Randall <joshua.randall@sanger.ac.uk>
* Andrey Kartashov <porter@porter.st>
* Dan Leehr <dan.leehr@duke.edu>
* Andrey Kartashov <Andrey.Kartashov@cchmc.org>
