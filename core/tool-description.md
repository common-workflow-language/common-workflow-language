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



### Runtime Requirements

### Document Author

[FOAF](http://www.foaf-project.org)
person entry for author of description document.

### Software Description

Software description field contains
[DOAP](https://github.com/edumbill/doap/wiki)
record that describes the application.

### EDAM Classification

