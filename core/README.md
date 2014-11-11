
[Tools](tool-description.md)

[Workflows](workflow-description.md)

[Runtime environment for tools](runtime-environment.md)

## Basic design

Current draft is based on a typical data-flow workflow model.
No cycles are allowed in the graph as loop constructs are replaced with automatic "parallel-for-each"
runs of individual workflow components.

Data passed between input/output ports of these components can be any JSON-compatible structure.
Files are encoded as a structure with URL/path pointer to the data,
 and additional metadata which includes accompanying index files.

For packaging tools and dependencies, we currently only support [Docker](http://docker.com) images.
