Common Workflow Language
========================

[![GitHub stars](https://img.shields.io/github/stars/common-workflow-language/common-workflow-language.svg)](https://github.com/common-workflow-language/common-workflow-language/stargazers) [![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/common-workflow-language/common-workflow-language?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

The Common Workflow Language (CWL) is a specification for describing analysis
workflows and tools that are portable and scalable across a variety of software
and hardware environments, from workstations to cluster, cloud, and high
performance computing (HPC) environments.  CWL is designed to meet the needs of
data-intensive science, such as Bioinformatics, Medical Imaging, Astronomy,
Physics, and Chemistry.

CWL is developed by an informal, multi-vendor working group consisting of
organizations and individuals interested enabling scientists to share data
analysis workflows.  [The CWL project is on Github.](https://github.com/common-workflow-language/common-workflow-language)

CWL builds on technologies such as [JSON-LD](http://json-ld.org)
for data modeling and [Docker](http://docker.com) for portable runtime
environments.

## User Guide

The [CWL user guide (v1.0)](http://www.commonwl.org/v1.0/UserGuide.html) provides a
gentle introduction to learning how to write CWL command line tool and workflow
descriptions.

## Specification

For developers and advanced users, the current
[CWL specification (v1.0)](http://www.commonwl.org/v1.0/) provides
authoritative documentation of the execution of CWL documents.  Links older
drafts:
[draft-1](https://github.com/common-workflow-language/common-workflow-language/tree/master/draft-1),
[draft-2](http://www.commonwl.org/draft-2/),
[draft-3](http://www.commonwl.org/draft-3/)

### Citation

Please cite https://dx.doi.org/10.6084/m9.figshare.3115156.v2

## Implementations

|Software|Description|CWL support|Platform support|Platform Maturity|
|--------|-----------|-----------|--------|--------|
|[cwltool](https://github.com/common-workflow-language/cwltool)|Reference implementation of CWL|[![Build Status](https://ci.commonwl.org/job/cwltool-conformance/badge/icon)](http://ci.commonwl.org/job/cwltool-conformance/lastBuild/testReport/)|Linux, OS X, local execution only|Production|
|[Arvados](https://arvados.org)|Distributed computing platform for data analysis on massive data sets. [Using CWL on Arvados](http://doc.arvados.org/user/cwl/cwl-runner.html)|[![Build Status](https://ci.commonwl.org/job/arvados-conformance/badge/icon)](http://ci.commonwl.org/job/arvados-conformance/lastBuild/testReport/)|AWS, GCP, Azure, Slurm|Production|
|[Toil](https://github.com/BD2KGenomics/toil)|Toil is a workflow engine entirely written in Python.|[![Build Status](https://ci.commonwl.org/job/toil-conformance/badge/icon)](http://ci.commonwl.org/job/toil-conformance/lastBuild/testReport/)|AWS, GCP, Azure, OpenStack, Grid Engine, Mesos|Production|
|[Rabix Bunny](https://github.com/rabix/bunny)|Reproducible Analyses for Bioinformatics|[![Build Status](https://ci.commonwl.org/buildStatus/icon?job=rabix-conformance)](https://ci.commonwl.org/job/rabix-conformance/)|Java|alpha|
|[Apache Taverna](http://taverna.incubator.apache.org/)|Domain-independent Workflow Management System|[alpha](https://issues.apache.org/jira/browse/TAVERNA-900)|Java|Production|
|[Galaxy](https://galaxyproject.org/)|Web-based platform for data intensive biomedical research.|[alpha](https://github.com/common-workflow-language/galaxy)|Python|Production|
|[AWE](https://github.com/MG-RAST/AWE)|Workflow and resource management system for bioinformatics data analysis.|[alpha](https://github.com/wgerlach/AWE)|Go|Production|
|[Funnel](https://github.com/bmeg/funnel)|Use Google Genomics Pipeline API with CWL|alpha|GCP|alpha|
|[xenon-cwl-runner](https://github.com/NLeSC/xenon-cwl-runner)|Run CWL workflows using Xenon|alpha|[any Xenon backend](http://nlesc.github.io/Xenon/): local, ssh, SLURM, Torque, Grid Engine|Production|


## Repositories of CWL Tools and Workflows

|Repository|Description|
|----|-----------|
|[Workflows repository](https://github.com/common-workflow-language/workflows)|Git repository of user contributed tools and workflows.|
|[Dockstore tool registry](http://dockstore.org)|An open platform for sharing Docker-based tools described with the Common Workflow Language used by the GA4GH.|

## Software for working with CWL

|Software|Description|
|--------|-----------|
|[cwltest](https://github.com/common-workflow-language/cwltest)|CWL testing framework,  automated testing of tools and workflows written with CWL|
|[cwl-upgrader](https://github.com/common-workflow-language/cwl-upgrader)|Upgrade CWL documents from draft-3 to v1.0|
|[argparse2tool](https://github.com/erasche/argparse2tool#cwl-specific-functionality)|Generate CWL CommandLineTool wrappers (and/or Galaxy tool descriptions) from Python programs that use argparse.  Also supports the [click](http://click.pocoo.org/5/) argument parser.|
|[cwl2argparse](https://github.com/common-workflow-language/cwl2argparse)|Generate Python argparse code from CWL CommandLineTool description.|
|[pypi2cwl](https://github.com/common-workflow-language/pypi2cwl)|Automatically run argparse2cwl on any package in PyPi|
|[cwlavro](https://github.com/common-workflow-language/cwlavro)|Java classes for loading CWL documents|
|[acd2cwl](https://github.com/common-workflow-language/acd2cwl)|CWL generator for ACD (EMBOSS) files |
|[CWLviewer](https://github.com/MarkRobbo/CWLViewer)|A web application to view and share Common Workflow Language workflows|

## Support, Community and Contributing

The recommended place to ask a question about all things CWL is on
[Biostars](https://www.biostars.org/t/cwl/).

[![Biostars CWL](https://www.biostars.org/static/biostar2.logo.png)](https://www.biostars.org/t/cwl/)

If you are interested in learning more or contributing ideas or code,
[come chat with us on Gitter](https://gitter.im/common-workflow-language/common-workflow-language),
check out [#CommonWL on Twitter](https://twitter.com/search?q=%23CommonWL),
join the [mailing list common-workflow-language on Google Groups](https://groups.google.com/forum/#!forum/common-workflow-language) or
[fork the repository](https://github.com/common-workflow-language/common-workflow-language)
and send a pull request!

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
