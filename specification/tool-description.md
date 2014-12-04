Common Workflow Language Tool Description, Draft 1
==================================================

# Introduction

A *tool* is a basic executable element of a workflow.  A tool is a standalone
program which is invoked on some input to perform computation, produce output,
and then terminate.  In order to use a tool in a workflow, it is necessary to
connect the inputs and outputs of the tool to upstream and downstream steps.
However because there tens of thousands of existing tools with enormous variety
in the syntax for invocation, input, and output, it is impossible for a
workflow to use these tools without additional information.  The purpose of the
tool description document is to formally describe the inputs and outputs of a
tool that is compatible with the workflow, and to describe how to translate
inputs to an actual program invocation.

# Concepts

The *tool description document* consists of five major parts: the input schema,
the output schema, the command line adapter, tool requirements, and tool metadata.

- The *input schema* formally describes the permissible fields and datatypes that
  make up input record.  Input fields follow the JSON data model, and may
  consist of string, number, boolean, object, or array values.  Files are
  represented as an object with a string field that is the locally-available
  path to the file.

- The *output schema* describes how to build the output record based on the output
  produced by an invocation of the tool.

- The *command line adapter* provides the template for generating a concrete
  command line invocation based on an input record.

- The *tool requirements* describes the hardware and software environment required
  to run the tool.

- The *tool metadata* consists of information about the tool, such as a human
  readable description, contact information for the author, software catalog
  entry, and so forth.

The *job order document* consists of an input record and an optional allocated
resources record.

- The *input record* are the concrete input values for an invocation of the
  tool.  It is validated against the input schema described in the tool
  document.

- The *allocated resources record* is a set of fields describing hardware
  resources available to run the tool, which should be compared to the tool
  requirements to determine if the minimum requirements are met.  This may
  alter the behavior of the tool, such as setting the number of threads to
  create based on the number of available CPU cores.

Together, the tool description document and the job order document provide all
the necessary information to actually set up the environment and build the
command line to run a specific invocation of the tool.

Tools are executed by the *workflow infrastructure*.  The workflow
infrastructure is the underlying platform responsible for interpreting the tool
description and job order, setting up the necessary runtime environment, and
actually invoking the tool process.  Provided that assumptions and restrictions
outlined below are met, the workflow infrastructure has broad leeway to
schedule tool invocations on remote cluster or cloud compute nodes, use virtual
machines or operating system containers to manage the runtime, and to use
remote or distributed file systems to manage input and output files.

When tool execution completes, the output record is built based on the output
schema.  The output schema includes *adapter* sections which describe how to
capture the tool output, or propagate values from input to output.

## Assumptions and restrictions

1. Tools run in a POSIX environment.

2. Tools must be non-interactive, command line programs.  Tools must not
   require any kind of console, GUI, or web based interaction in order to start
   and run to completion.

3. Tool input comes from the command line, environment variables, the
   standard input stream, by reading files, or by accessing network resources.

4. Tool output is emitted via the standard output stream, by writing files, or
   by accessing a network resource.

5. Tools do not access hardware devices.

6. Input files are read-only.  Tools do not modify existing files, only create
   new ones.

7. Tool may only write files to a designated output directory or designated
   scratch space.

8. Tool may be multithreaded or spawn child processes, however when the
   original tool process exits, the tool is considered finished.

9. By normal POSIX semantics, a tool exit code of 0 is considered success, and
   a non-zero exit code is considered an error.

# Syntax

_(Note: everything after this is old and remains to be updated)_

The tool description document is written in [JSON](http://json.org) format.

## Input schema

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


## Output schema

Describes files that are generated in the process of execution. Also uses JSON-Schema.

Adapter section of individual outputs consists of a glob expression (to capture generated files),
 as well as "meta" and "indices" fields used to describe metadata of generated files.


## Command line adapter

An array of either string literals or expressions that generates the executable path and process arguments.
Annotated inputs will map onto process arguments which are appended to this list.
Value for the ```stdout``` field is a string or expression that specifies a file name where stdout is piped.


## Tool requirements

* Container specification (currently just location of docker image).
* Computation resources (CPU, RAM, Network).
* Platform features (enumeration of non-standard platform features).

## Tool metadata

### Document Author

Name and contact detail of an author of description document.

Example:

```jsonld
{
  "@context": "http://xmlns.com/foaf/context",
  "@id" : "http://orcid.org/0000-0002-1825-0097",
  "name": "John Smith",
  "email": "j.smith@example.com"
}
```

The `@id` SHOULD be an [ORCID](http://orcid.org/) identifier, but MAY be any other [Web-ID](http://www.w3.org/TR/webid/).

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

# Command line generation algorithm

TBD.
