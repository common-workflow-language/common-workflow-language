Common Workflow Language
========================

This repo holds an approximate description of the specification being developed on the
[Common Workflow Language mailing list](https://groups.google.com/forum/#!forum/common-workflow-language).

CWL is an informal task force consisting of people from various organizations that have an interest in portability
 of bioinformatics workflows.
The goal is to specify a way to describe bioinformatics tools and workflows that is powerful,
 easy to use and allows for portability of tools/workflows and reproducibility of runs.


## Basic design

Current draft is based on a typical data-flow workflow model.
No cycles are allowed in the graph as loop constructs are replaced with automatic "parallel-for-each"
runs of individual workflow components.

Data passed between input/output ports of these components can be any JSON-compatible structure.
Files are encoded as a structure with URL/path pointer to the data,
 and additional metadata which includes accompanying index files.

For packaging tools and dependencies, we currently only support [Docker](http://docker.com) images.


## More details

[Tools](core/tool-description.md)

[Workflows](core/workflow-description.md)

[Runtime environment for tools](core/runtime-environment.md)


## Contributing

If you are interested in contributing ideas or code,
 join the [mailing list](https://groups.google.com/forum/#!forum/common-workflow-language).
