Tool Description
================

Tool is an atomic executable element of a workflow.
It represents a software application and accompanying description.
Tool description is a
[JSON-LD](http://www.w3.org/TR/2014/REC-json-ld-20140116/)
document that enables its inclusion in workflows, execution and UI generation.

## Basic file format

Tool description can conceptually be split into these parts:


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
the input is translated to command line argument;
basic types are extended with a literal "file".


Example:
```json
{
  "type": "object",
  "required": ["input1", "param1"],
  "properties": {
    "input1": {
      "type": "file",
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
      "items": {"type": "string"},
      "adapter": {
        "order": 1,
        "itemSeparator": ","
      }
    }
  }
}
```


### Output description

Describes files that are generated in the process of execution. Also uses JSON-Schema.

Adapter section of individual outputs consists of a glob expression (to capture generated files),
 as well as "meta" and "indices" fields used to describe metadata of generated files.


### Command line adapter

An array of either string literals or expressions that generates the executable path and process arguments.
Annotated inputs will map onto process arguments which are appended to this list.
Value for the ```stdout``` field is a string or expression that specifies a file name where stdout is piped.


### Requirements

* Container specification (currently just location of docker image).
* Computation resources (CPU, RAM, Network).
* Platform features (enumeration of non-standard platform features).


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

Software description field contains a
[DOAP](https://github.com/edumbill/doap/wiki)
record that describes the application.
Mandatory fields are `name`, `version` and `licence`.

Example:

```jsonld
{
  "@context": {"@vocab": "http://usefulinc.com/ns/doap#"},
  "name": "My Aligner",
  "homepage": "http://example.com/ma",
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


## Expressions

Some fields may contain
[ECMAScript 5.1](http://www.ecma-international.org/ecma-262/5.1/)
expressions as values.
They are used for basic string manipulation when generating the command line,
 creating output structures (metadata and indices) and dynamic resource requirements.

The order of evaluation is undefined.
