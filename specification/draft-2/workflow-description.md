
Author:

* Peter Amstutz <peter.amstutz@curoverse.com>, Curoverse

Contributers:

* Nebojsa Tijanic <nebojsa.tijanic@sbgenomics.com>, Seven Bridges Genomics
* Luka Stojanovic <luka.stojanovic@sbgenomics.com>, Seven Bridges Genomics
* John Chilton <jmchilton@gmail.com>, Galaxy Project, Pennsylvania State University
* Michael Crusoe <michael.crusoe@gmail.com>, Michigan State University
* Hervé Ménager <herve.menager@gmail.com>, Institut Pasteur
* Maxim Mikheev <mikhmv@biodatomics.com>, BioDatomics
* Stian Soiland-Reyes <soiland-reyes@cs.manchester.ac.uk>, University of Manchester

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
* [Uniform Resource Identifier (URI): Generic Syntax](https://tools.ietf.org/html/rfc3986)

## Scope

This document describes the CWL syntax, execution, and object model.  It
is not intended to document a specific implementation of CWL, however it may
serve as a reference for the behavior of conforming implementations.

## Terminology

The terminology used to describe CWL documents is defined in the
Concepts section of the specification. The terms defined in the
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
**fields**) and where the name is a string and the value is a string, number,
boolean, array, or object.

A **document** is a file containing a serialized object.

A **process** is a basic unit of computation.  It accepts some input data,
performs some computation, produces a some output data.

A **input object** is a object describing the inputs to a invocation of process.

A **output object** is a object describing the output of an invocation of a process.

A **input schema** describes the valid format (required fields, data types)
for an input object.

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
or workflow platform unless explicitly declared though the use of [process
requirements](#/schema/ProcessRequirement).

# Syntax

Documents containing CWL objects are serialized and loaded using YAML syntax.
A conforming implementation must accept all valid YAML documents.

A CWL document may be formally validated using the Avro schema located at:

https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl-avro.yml

An implementation may interpret a CWL document as [JSON-LD](http://json-ld.org)
and convert a CWL document to a [Resource Definition Framework
(RDF)](http://www.w3.org/RDF/) graph using the context located at:

https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl-context.json

An implementation may reason about the resulting RDF graph using the RDF Schema
located at:

https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl-rdfs.jsonld

## Identifiers and references

If an object contains an `id` field, that is used to uniquely identify the
object in that document.  The value of the `id` field must be unique over the
entire document.  The format of the `id` field is that of a [relative fragment
identifier](https://tools.ietf.org/html/rfc3986#section-3.5), and must start
with a hash `#` character.

Where an object field permits a [`Ref`](#/schema/Ref) value containing a
fragment identifier, the implementation must look up object using the
referenced `id` field.

An implementation may choose to only honor references to objects for which the
`id` field is explicitly listed in this specification.

# Execution

The generic execution sequence of a CWL document is as follows.  The root
object defined in a CWL document must be a [`Process`](#/schema/Process)
object.

1. Load and validate CWL document, yielding a process object.
2. Load input object.
3. Validate input object against the `inputs` defined by the process.
4. Validate that process requirements are met.
5. Perform any further setup required by the specific process type.
6. Execute the process.
7. Build output object to capture results of process execution.
8. Validate output object against the `outputs` defined by the process.
9. Report output object to the caller.

## Expressions

An expression is a fragment of executable code which is evaluated by workflow
platform to affect the inputs, outputs, or behavior of a process.  In the
generic execution sequence, expressions may be evaluated during step 5 (process
setup), step 6 (execute process), and/or step 7 (build output).

# Objects
