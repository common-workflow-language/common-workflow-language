
Authors:

* Peter Amstutz <peter.amstutz@curoverse.com>, Curoverse
* Nebojsa Tijanic <nebojsa.tijanic@sbgenomics.com>, Seven Bridges Genomics

# Abstract

A Workflow is an analysis task which uses a directed graph to represent a
sequence of operations that transform an input data set to output.  This
specification defines the Common Workflow Language (CWL), a vendor-neutral
standard for representing Workflows intended to be portable across a variety of
computing platforms.  This specification defines two concrete workflow
operations, the Comand Line Tool, for invoking a command line program
(optionally within an operating system container) and capturing the output, and
the Expression Tool, for applying ECMAScript functions to the data set.

# Status of This Document

This document is the product of the [Common Workflow Language working
group](https://groups.google.com/forum/#!forum/common-workflow-language).  The
latest version of this document is available in the "specification" directory at

https://github.com/common-workflow-language/common-workflow-language

The products of the CWL working group (including this document) are made available
under the terms of the Apache License, version 2.

# Table of Contents

# Introduction

The Common Workflow Language (CWL) working group is an informal, multi-vendor
working group consisting of various organizations and individuals that have an
interest in portability of data analysis workflows.  The goal is to create
specifications like this one that enable data scientists to describe analysis
tools and workflows that are powerful, easy to use, portable, and support
reproducibility.

## Introduction to draft 2

This specification represents the second milestone of the CWL group.  Since
draft-1, this draft introduces a number of major changes and additions:

* Use of Avro schema (instead of JSON-schema) and JSON-LD for data modeling
* Significant refactoring of the Command Line Tool description.
* Initial data and execution model for Workflows.

## Purpose

CWL is designed to express workflows for data-intensive science, such as
Bioinformatics, Chemistry, Physics, and Astronomy.  This specification is
intended to define a data and execution model for Workflows and Command Line
Tools that can be implemented on top of a variety of computing platforms,
ranging from individual workstation to cluster, grid, cloud, and high
performance computing systems.

## Dependencies on Other Specifications

* [JSON](http://json.org)
* [JSON-LD](http://json-ld.org)
* [YAML](http://yaml.org)
* [Avro](https://avro.apache.org)
* [ECMAScript 5.1 (Javascript)](http://www.ecma-international.org/ecma-262/5.1/)

## Scope

This document describes the CWL syntax, data and execution model.  It
is not intended to document a specific implementation of CWL, however it may
serve as a reference for the behavior of conforming implementations.

## Terminology

The terminology used to describe CWL documents is defined in the
[Concepts](#concepts) section of the specification. The terms defined in the
following list are used in building those definitions and in describing the
actions of an CWL implementation:

**may**: Conforming CWL documents and CWL implementations are permitted to but need
not behave as described.

**must**: Conforming CWL documents and CWL implementations are required to behave
as described; otherwise they are in error.

**error**: A violation of the rules of this specification; results are
undefined. Conforming implementations may detect and report a error and may
recover from it.

**fatal error**: A violation of the rules of this specification; results are
undefined. Conforming implementations must not continue to execute the current
process and may report an error.

**at user option**: Conforming software may or must (depending on the modal verb in
the sentence) behave as described; if it does, it must provide users a means to
enable or disable the behavior described.


# Concepts

## Data

A **object** is a data structure equivalent to the "object" type in JSON,
consisting of a unordered set of name/value pairs (referred to here as
*fields*) and where the name is a string and the value is a string, number,
boolean, array, or object.

A **document** is a file containing a serialized object.

A **process** is the basic unit of computation.  It accepts some input data,
performs some computation, produces a some output data.

A **input object** is a object describing the inputs to a invocation of process.

A **output object** is a object describing the output of an invocation of a process.

A **input schema** describes valid format (required fields, data types)
  for a input object.

A **output schema** describes the valid format for a output object.

## Execution

A **command line tool** is a process characterized by the
execution of a standalone, non-interactive program which is invoked on some
input, produces output, and then terminates.

A **workflow** is a process characterized by multiple subprocesses, where
subprocess outputs are connected to the inputs of other downstream
subprocesses, and independent subprocesses may run concurrently.

A **runtime environment** is the actual hardware and software environment when
executing a command line tool.  It includes, but is not limited to, the
hardware architecture, hardware resources, operating system, software runtime
(if applicable, such as the Python interpreter or the JVM), libraries, modules,
packages, utilities, and data files required to run the tool.

A **workflow platform** is a specific hardware and software and implementation
capable of interpreting a CWL document and executing the processes specified by
the document.  The responsibilities of the workflow infrastructure may include
scheduling process invocation, setting up the necessary runtime environment,
making input data available, invoking the tool process, and collecting output.

It is intended that the workflow platform has broad leeway outside of this
specification to optimize use of computing resources and enforce policies not
covered by this specifcation.  Some of areas are out of scope for CWL that may
be handled by a specific workflow platform are:

* Data security and permissions.
* Scheduling tool invocations on remote cluster or cloud compute nodes.
* Using virtual machines or operating system containers to manage the runtime
  (except as described in [Executing tools in
  Docker](#executing-tools-in-docker))
* Using remote or distributed file systems to manage input and output files.
* Translating or rewrite file paths.
* Determining if a process has already been executed and can be skipped and
  re-use previous results.
* Pausing and resume processes or workflows.

Conforming CWL documents must not assume anything about the runtime environment
or workflow platform unless explicitly declared though the use of
[Requirements](#requirements) or [Hints](#hints).


# Syntax

Documents containing CWL objects are serialized and loaded using YAML syntax.
A conforming implementation must accept all valid YAML documents.

A CWL document may be formally validated using the Avro schema located at:

https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl.avsc

An implementation may interpret a CWL document as [JSON-LD](http://json-ld.org)
and convert a CWL document to a [Resource Definition Framework
(RDF)](http://www.w3.org/RDF/) graph using the context located at:

https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl-context.json

An implementation may reason about the resulting RDF graph using the RDF Schema
located at:

https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl-rdfs.jsonld


# Data types

CWL data types are based on Avro schema declarations.  The data types used in
CWL are briefly listed below.  Refer to the [Avro schema declaration
documentation](https://avro.apache.org/docs/current/spec.html#schemas) for
detailed information.  In addition, CWL also defines [`File`](#file) as a
special record type, described below.

## Primitive types

Name|Description
----|-----------
null|no value
boolean|a binary value
int|32-bit signed integer
long|64-bit signed integer
float|single precision (32-bit) IEEE 754 floating-point number
double|double precision (64-bit) IEEE 754 floating-point number
bytes|sequence of 8-bit unsigned bytes
string|unicode character sequence

## Complex types

Name|Description
----|-----------
record|An object with one or more fields defined by name and type
enum|A value from a finite set of symbolic values
array|An ordered sequence of values
map|An unordered collection of key/value pairs

## File object


# Object model

## Process

To execute a CWL document means to execute the `Process` object defined by the
document.

Field|Data type|Default
-----|---------|-------
`class`|enum one of [`CommandLineTool`](#command-line-tools), [`ExpressionTool`](#expression-tools), [`Workflow`](#workflows), [`External`](#external-process-definitions)|External
`inputs`|array of [`InputSchema`](#input-schema)|none (required field)
`outputs`|array of [`OutputSchema`](#output-schema)|none (required field)
`schemaDefs`|array of [`SchemaDef`](#schema)|null

The type of process is defined by the `class` field.  Valid values for this
field are [`CommandLineTool`](#command-line-tools),
[`ExpressionTool`](#expression-tools), [`Workflow`](#workflows) or
[`External`](#external-process-definitions).  If the `class` field is not
specified, the implementation must default to the process class `External`.

Process objects must include `inputs` and `outputs`.  These define the input
and output parameters of the process, and must be used to validate the input
object and generate and validate the output object.

Process objects may include the `schemaDefs` field.  This field consists of an
array of type definitions which must be used when interpreting the `inputs` and
`outputs` fields.  When a symbolic type is encountered that is not in the
[Datatype](#datatype) enum described above, the implementation must check if
the type is defined in schemaDefs and use that definition.  If the type is not
found in schemaDefs, it is an error.  The entries in schema definitions must be
processed in the order listed such that later schema definitions may refer to
earlier schema definitions.

## External process definitions

An external process provides a level of indirection to instantiate a process
defined by an external resource (another CWL document).

Field|Data type|Default
-----|---------|-------
`impl`|URI|none, required

The `impl` field specifies the resource that should be loaded to find the
actual process.

## Schema

Field|Data type|Default
-----|---------|-------
`id`|fragment URI|null
`name`|string|none, required when part of `schemaDefs` or `record`
`def`|URI|none, required when part of `inputs` or `outputs` of [`External`](#external-process-definitions)
`type`|[`Datatype`](#data-types), [`Schema`](#schema), string, or array of [`Datatype`](#data-types), [`Schema`](#schema), string|none, required
`fields`|array of [`Schema`](#schema)|null, required when `type` is `record`
`symbols`|array of [`Schema`](#schema)|null, required when `type` is `enum`
`items`|[`Datatype`](#data-types), [`Schema`](#schema), string, or array of [`Datatype`](#data-types), [`Schema`](#schema), string|null, required when `type` is `array`
`values`|[`Datatype`](#data-types), [`Schema`](#schema), string, or array of [`Datatype`](#data-types), [`Schema`](#schema), string|null, required when `type` is `map`
`commandLineBinding`|[`CommandLineBinding`](#command-line-binding)|null, used when process object is [`CommandLineTool`](#command-line-tools)
`outputBinding`|[`OutputBinding`](#output-binding)|null, used when process object is [`CommandLineTool`](#command-line-tools)



## References

## Expressions


# Command line tools

## Command line binding

## Output binding

## Executing tools in Docker

# Expression tools

# Workflows
