Common Workflow Language
========================

The Common Workflow Language (CWL) is an informal, multi-vendor working group
consisting of various organizations and individuals that have an interest in
portability of data analysis workflows.  Our goal is to create specifications
that enable data scientists to describe analysis tools and workflows that are
powerful, easy to use, portable, and support reproducibility.

CWL builds on technologies such as [JSON-LD](http://json-ld.org)
for data modeling and [Docker](http://docker.com) for portable runtime\
environments.

CWL is designed to express workflows for data-intensive science, such as
Bioinformatics, Medical Imaging, Chemistry, Physics, and Astronomy.

## CWL User Guide

[User guide for the current stable specification (v1.0)](http://www.commonwl.org/v1.0/UserGuide.html),
provides a gentle introduction to writing CWL command line tool and workflow descriptions.

## CWL Specification

The current stable specification is [v1.0](http://www.commonwl.org/v1.0/):

http://www.commonwl.org/v1.0/

Older drafts: [draft-1](https://github.com/common-workflow-language/common-workflow-language/tree/master/draft-1), [draft-2](http://www.commonwl.org/draft-2/), [draft-3](http://www.commonwl.org/draft-3/)

### Citation

Please cite https://dx.doi.org/10.6084/m9.figshare.3115156.v2

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
* [Apache Taverna](http://taverna.incubator.apache.org/),
  [Apache Taverna wiki page](https://github.com/common-workflow-language/common-workflow-language/wiki/Taverna)

We continuously run the CWL conformance tests on several implementations:

https://ci.commonwl.org

## Examples

[Github repository of example tools and workflows.](https://github.com/common-workflow-language/workflows)

## Support

The best place to ask a question about all things CWL is on
[Biostars](https://www.biostars.org/t/cwl/).

[![Biostars
CWL](https://www.biostars.org/static/biostar2.logo.png)](https://www.biostars.org/t/cwl/)
</a>

## Development and testing

[The CWL project is on Github.](https://github.com/common-workflow-language/common-workflow-language)

[![GitHub
stars](https://img.shields.io/github/stars/common-workflow-language/common-workflow-language.svg)](https://github.com/common-workflow-language/common-workflow-language/stargazers)

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

Your CWL Community Engineer, Michael R. Crusoe, publishes a blog about his work
with updates at http://mrc.commonwl.org.

### Code of Conduct

The CWL Project is dedicated to providing a harassment-free experience for
everyone, regardless of gender, gender identity and expression, sexual
orientation, disability, physical appearance, body size, age, race, or
religion. We do not tolerate harassment of participants in any form.

This code of conduct applies to all CWL Project spaces, including the Google
Group, the Gitter chat room, the Google Hangouts chats, both online and off.
Anyone who violates this code of conduct may be sanctioned or expelled from
these spaces at the discretion of the leadership team.

For more details, see our [Code of
Conduct](https://github.com/common-workflow-language/common-workflow-language/blob/master/CODE_OF_CONDUCT.md)

## Participating Organizations

* [Curoverse](http://curoverse.com)
* [Seven Bridges Genomics](http://sbgenomics.com)
* [Galaxy Project](http://galaxyproject.org/)
* [Apache Taverna](http://taverna.incubator.apache.org/)
* [Institut Pasteur](http://www.pasteur.fr)
* [Wellcome Trust Sanger Institute](https://www.sanger.ac.uk/)
* [University of California Santa Cruz](https://cbse.soe.ucsc.edu/research/bioinfo)
* [Harvard Chan School of Public Health](http://www.hsph.harvard.edu/)
* [Cincinnati Children's Hospital Medical Center](http://www.cincinnatichildrens.org/)
* [Broad Institute](https://www.broadinstitute.org)
* [BioDatomics](http://www.biodatomics.com/)
* [Wolfson Wohl Cancer Research Centre](http://www.gla.ac.uk/researchinstitutes/cancersciences/ics/facilities/wwcrc/)

## Individual Contributors

(Alphabetical)

* Peter Amstutz <peter.amstutz@curoverse.com>
* Robin Andeer <robin.andeer@gmail.com>
* Brad Chapman <bchapman@hsph.harvard.edu>
* John Chilton <jmchilton@gmail.com>
* Michael R. Crusoe <michael.crusoe@gmail.com>
* Roman Valls Guimerà <brainstorm@nopcode.org>
* Guillermo Carrasco Hernandez <guille.ch.88@gmail.com>
* Sinisa Ivkovic <sinisa.ivkovic@sbgenomics.com>
* Andrey Kartashov <Andrey.Kartashov@cchmc.org>
* John Kern <kern3020@gmail.com>
* Dan Leehr <dan.leehr@duke.edu>
* Hervé Ménager <herve.menager@gmail.com>
* Maxim Mikheev <mikhmv@biodatomics.com>
* Tim Pierce <twp@unchi.org>
* Josh Randall <joshua.randall@sanger.ac.uk>
* Janko Simonović <janko.simonovic@sbgenomics.com>
* Stian Soiland-Reyes <soiland-reyes@cs.manchester.ac.uk>
* Luka Stojanovic <luka.stojanovic@sbgenomics.com>
* Nebojša Tijanić <nebojsa.tijanic@sbgenomics.com>
