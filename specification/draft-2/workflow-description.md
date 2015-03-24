Common Workflow Language, Draft 2
=================================

Authors:
* Peter Amstutz <peter.amstutz@curoverse.com>, Curoverse
* Nebojsa Tijanic <nebojsa.tijanic@sbgenomics.com>, Seven Bridges Genomics

# Abstract

A Workflow is an analysis task which uses a directed graph to represent a
sequence of operations that transform an input data set to output.  This
specification defines the Common Workflow Language (CWL), a vendor-neutral
standard for representing Workflows intended to be portable across multiple
analytical computing platforms.  This specification defines two concrete
workflow operations, the Comand Line Tool, for invoking a command line program
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

1. [Introduction](#introduction)
  1. [Introduction to draft 2](#introduction-to-draft-2)
  2. [Purpose](#purpose)
  3. [Dependencies on Other Specifications](#dependencies-on-other-specifications)
  4. [Requirements](#requirements)
  5. [Scope](#scope)
  6. [Terminology](#terminology)
2. [Concepts](#concepts)
3. [Syntax](#syntax)
4. [Data model](#data-model)
  1. [Parameters](#parameters)
  2. [Files](#files)
5. [Execution model](#execution-model)
6. [Process types](#process-types)
  1. [Workflow](#workflow)
  2. [CommandLineTool](#commandlinetool)
  3. [ExpressionTool](#expressiontool)

# Introduction

## Introduction to draft 2

## Purpose

## Dependencies on Other Specifications

[JSON](http://json.org)
[JSON-LD](http://json-ld.org)
[YAML](http://yaml.org)
[Avro](https://avro.apache.org/docs/current/spec.html)

## Requirements

## Scope

## Terminology

The terminology used to describe CWL documents is defined in the
[Concepts](#concepts) section of the specification. The terms defined in the
following list are used in building those definitions and in describing the
actions of an CWL implementation:

may: Conforming CWL documents and CWL implementations are permitted to but need
not behave as described.

must: Conforming CWL documents and CWL implementations are required to behave
as described; otherwise they are in error.

error: A violation of the rules of this specification; results are
undefined. Conforming implementations may detect and report a error and may
recover from it.

at user option: Conforming software may or must (depending on the modal verb in
the sentence) behave as described; if it does, it must provide users a means to
enable or disable the behavior described.


# Concepts

- A *process* is the basic unit of computation.  It accepts some input data,
performs some computation, produces a some output data.

- A *object* is a data structure equivalent to the "object" type in JSON,
consisting of a unordered set of name/value pairs (referred to here as
*fields*) and where the name is a string and the value is a string, number,
boolean, array, or object.

- A *document* is a file containing a serialized object.

- A *job order* is a object describing the inputs to a invocation of process.

- A *output record* is a object describing the output of an invocation of a process.

- A *input schema* describes valid format (required fields, data types)
  for a job order.

- A *output schema* describes the valid format for the output object.

- A *command line tool* is a process characterized by the
execution of a standalone, non-interactive program which is invoked on some
input, produces output, and then terminates.

- A *workflow* is a process characterized by multiple subprocesses, where
subprocess outputs are connected to the inputs of other downstream
subprocesses, and independent subprocesses may run concurrently.

# Syntax

Documents containing CWL objects are serialized and loaded using
[YAML](http://www.yaml.org/) syntax.  A conforming implementation must accept
all valid YAML documents.

# Data model

## Schemas

The CWL object model is formally defined using [Avro
schema](https://avro.apache.org/docs/current/spec.html) and is available at
<https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl.avsc>

An implementation may interpret the CWL object as [JSON-LD](http://json-ld.org)
using the context specified at
<https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl-context.json>
to convert a CWL document to a [Resource Definition Framework
(RDF)](http://www.w3.org/RDF/) graph.  An implementation may reason about the
resulting RDF graph using the RDF Schema specified at
<https://github.com/common-workflow-language/common-workflow-language/blob/master/schemas/draft-2/cwl-rdfs.jsonld>

## Process objects

Process parameters

### Files

# Execution model

# Workflow processes

# Command line tool processes

## Executing tools in Docker

# Expression tool processes
