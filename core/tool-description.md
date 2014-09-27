Tool Description
================

Tool is an atomic executable element of a workflow. It represents a software application and description.
Tool description is a
[JSON-LD](http://www.w3.org/TR/2014/REC-json-ld-20140116/)
document that enables its inclusion in workflows, scheduling and execution.

Tool description contains these parts:

### Inputs Description

Inputs are described using [JSON Schema](http://json-schema.org).
JSON Schema type for `inputs` field MUST be `object`.

### Output description

Describes files that are generated in the process of execution.

### Command line specification

Procedural or declarative description of how to run a tool via command line.

### Runtime Requirements

Computation resources, platform features...

### Document Author

Name and contact detail of an author of description document.

Example:

```jsonld
{
  "@context": "http://xmlns.com/foaf/context",
  "name": "John Smith",
  "email": "j.smith@example.com"
}
```

### Software Description

Software description field contains
[DOAP](https://github.com/edumbill/doap/wiki)
record that describes the application.
Mandatory fields are `name`, `version` and `licence`.

Example:

```jsonld
{
  "@context": {"@vocab": "http://usefulinc.com/ns/doap#"},
  "name": "My aWesome Aligner",
  "homepage": "http://example.com/mwa",
  "version": "0.1",
  "licence": "http://spdx.org/licenses/GPL-2.0+",
  "maintainer": {
    "@context": "http://xmlns.com/foaf/context",
    "name": "John Smith",
    "email": "j.smith@example.com"
  }
}
```


### EDAM Classification

TBD.
