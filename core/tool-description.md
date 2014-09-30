Tool Description
================

Tool is an atomic executable element of a workflow.
It represents a software application and accompanying description.
Tool description is a
[JSON-LD](http://www.w3.org/TR/2014/REC-json-ld-20140116/)
document that enables its inclusion in workflows, scheduling, execution and UI generation.

## Basic file format

Tool description can conceptually be splitted into these parts:


### Context and ID

In order for tool description to be a valid JSON-LD document,
context and ID should be specified.

Example:

```jsonld
{
  "@context": "http://example.com/contexts/draft01/tool",
  "@id": "http://example.com/tools/mwa"
}
```

### Inputs Description

Inputs are described using [JSON Schema](http://json-schema.org).
JSON Schema type for `inputs` field must be `object`.
Basic schema is extended with `adapter` key that describes how
the input is translated to command line argument.


Example:
```json
{
  "type": "object",
  "required": ["input1", "param1"],
  "properties": {
    "input1": {
      "type": {"$ref": "https://raw.githubusercontent.com/rabix/common-workflow-language/master/schemas/file"},
      "adapter": {"order": 2}
    },
    "param1": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "adapter": {
        "prefix": "-p",
        "separator": " ",
        "order": 1
      }
    },
    "param2": {
      "type": "array",
      "items" {"type": "string"},
      "adapter": {
        "order": 1,
        "itemSeparator": ","
      }
    }
  }
}
```


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


## JSON Evaluation

There are several things to note while processing tool description JSON.
Tool description relies on
[JSON references](https://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03)
and any such reference must be resolved prior to further processing.
The description may also contain
[ECMAScript 5.1](http://www.ecma-international.org/ecma-262/5.1/)
expressions as values.
Those expressions should be evaluated in accordance with rules outlined in
[runtime environment](runtime-environment.md)
specification.
