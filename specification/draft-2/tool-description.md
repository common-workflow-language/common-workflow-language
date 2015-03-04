Common Workflow Language Tool Description, Draft 2
==================================================

# Introduction

A *tool* is a basic executable element of a workflow.  A tool is a standalone
program which is invoked on some input to perform computation, produce output,
and then terminate.  In order to use a tool in a workflow, it is necessary to
connect the inputs and outputs of the tool to upstream and downstream steps.
However, because there are tens of thousands of existing tools with enormous variety
in the syntax for invocation, input, and output, it is impossible for a
workflow to use tools from different environments without additional information.  The purpose of the
tool description document is to formally describe the inputs and outputs of a
tool that is compatible with the workflow, and to describe how to translate
inputs to an actual program invocation.

# Concepts

In this specification, a *record* refers to a data structure consisting of a
unordered set of key-value pairs (referred to here as *fields*), where the keys
are unique strings.  This is functionally equivalent to a JSON "object", python
"dict", or the "hash" or "map" datatypes available in most programming
language.  A *document* is a file containing a serialized record written as JSON.

The *tool description document* consists of five major parts: the input schema,
the output schema, the command line adapter, tool requirements, and tool
metadata.  The exact syntax and semantics is discussed below in [Syntax](#Syntax).

- The *input schema* formally describes the permissible fields and datatypes of
  the field values that make up input record.  Input fields follow the JSON
  data model, and may consist of string, number, boolean, object, or array
  values.  Files are represented as an object with a string field that is the
  locally-available path to the file.

- The *command line adapter* provides the template for generating a concrete
  command line invocation based on an input record.

- The *tool requirements* describes the hardware and software environment required
  to run the tool.

- The *output schema* describes how to build the output record based on the output
  produced by an invocation of the tool.

- The *tool metadata* consists of information about the tool, such as a human
  readable description, contact information for the author, software catalog
  entry, and so forth.

The [*job order document*](#job-order-document) specifies the inputs
and environment for executing an instance of the tool.  It consists of
an *input record* and an optional *allocated resources record* (see
the [job order document specification](#job-order-document) for
details of these records).

Together, the tool description document and the job order document provide all
the necessary information to actually set up the environment and build the
command line to run a specific invocation of the tool.

The *runtime environment* is the hardware and software platform on
which the tool is run.  It includes, but is not limited to, the
hardware architecture, hardware resources, operating system, software
runtime (if applicable, such as the Python interpreter or the JVM),
libraries, modules, packages, utilities, and data files required to
run the tool.

Tools are executed by the *workflow infrastructure*, which is the platform responsible for interpreting the tool
description and job order, setting up the necessary runtime environment, and
actually invoking the tool process.  Provided that assumptions and restrictions
outlined below are met, the workflow infrastructure has broad leeway to
schedule tool invocations on remote cluster or cloud compute nodes, use virtual
machines or operating system containers to manage the runtime, to use remote or
distributed file systems to manage input and output files, and rewrite file
paths on the command line.

When tool execution completes, the output record is built based on the output
schema.  The output schema includes *adapter* sections which describe how to
capture the tool output, or propagate values from input to output.

# Execution

A *tool command line* is built based on the [adapter fields](#command-line-adapter) from the
tool description document and the values contained in [job order document](#job-order-document).

The executable program run by this tool is specified by the `baseCmd`
field in the command line adapter.  This field must identify a file
with the POSIX execute bit set.  If `baseCmd` does not include a path
separator character, the runtime environment's `$PATH` environment
variable is searched to find the absolute path of the executable.
Relative paths are not permitted.

The `TMPDIR` environment variable should be set in the runtime environment to
the designated temporary directory (scratch space).  Any files written to that
location should be deleted by the workflow infrastructure when the tool instance is complete.

Output files produced by tool execution must be written to the
*designated output directory*, which is the runtime environment's
current working directory when the tool begins executing.  The
designated output directory is empty except for "job.cwl.json", which
contains the job order record.

## Assumptions and restrictions

1. Tools run in a POSIX environment.

2. Tools must be non-interactive, command line programs.  Tools must not
   require any kind of console, GUI, or web based user interaction in order to
   start and run to completion.

3. Tool input must come from: the command line, the standard input
   stream, by reading input files, and/or by accessing network
   resources.

4. Tool input files and directories must be listed in the input record,
   or be part of an explicitly declared runtime environment.

5. Tool output is emitted via the standard output stream, by writing files, or
   by accessing a network resource.

6. Tool input files are read-only.  Tools do not modify existing files, only
   create new ones (see [TODO](#TODO)).

7. Tool output files are written only to the designated output
   directory or designated scratch space.

8. Tools may be multithreaded or spawn child processes; however, when
   the original tool process exits, the tool is considered finished
   regardless of whether any detached child processes are still
   running.

9. Tools do not access hardware devices.

## Job order document

The job order document consists of two fields: "inputs" and "allocatedResources".

- The "inputs" field is a record providing the concrete input values
  for an invocation of the tool. These input values are validated
  against the [input schema](#input-schema) described in the tool
  document.

- The "allocatedResources" field is a record describing the maximum
  hardware resources available to run the tool.  It is compared with
  the [tool resource requirements](#resources) to determine if the
  tool can run.  The fields are the same as those described in [tool
  resource requirements](#resources).

### Example

```json
{
  "inputs": {
    "input1": {
      "path": "../files/input1.fasta",
      "size": 678599850,
      "checksum": "sha1$6809bc2706188b7b10d99d06fe4f175f8fe8061a",
      "metadata": {
        "fileType": "fasta"
      }
    }
  },
  "allocatedResources": {
    "cpu": 4,
    "mem": 5000
  }
}
```

# Syntax
