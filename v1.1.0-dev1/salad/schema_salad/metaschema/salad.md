# Semantic Annotations for Linked Avro Data (SALAD)

Author:

* Peter Amstutz <peter.amstutz@curoverse.com>, Curoverse

Contributors:

* The developers of Apache Avro
* The developers of JSON-LD
* Nebojša Tijanić <nebojsa.tijanic@sbgenomics.com>, Seven Bridges Genomics

# Abstract

Salad is a schema language for describing structured linked data documents
in JSON or YAML documents.  A Salad schema provides rules for
preprocessing, structural validation, and link checking for documents
described by a Salad schema.  Salad builds on JSON-LD and the Apache Avro
data serialization system, and extends Avro with features for rich data
modeling such as inheritance, template specialization, object identifiers,
and object references.  Salad was developed to provide a bridge between the
record oriented data modeling supported by Apache Avro and the Semantic
Web.

# Status of This Document

This document is the product of the [Common Workflow Language working
group](https://groups.google.com/forum/#!forum/common-workflow-language).  The
latest version of this document is available in the "schema_salad" repository at

https://github.com/common-workflow-language/schema_salad

The products of the CWL working group (including this document) are made available
under the terms of the Apache License, version 2.0.

<!--ToC-->

# Introduction

The JSON data model is an extremely popular way to represent structured
data.  It is attractive because of its relative simplicity and is a
natural fit with the standard types of many programming languages.
However, this simplicity means that basic JSON lacks expressive features
useful for working with complex data structures and document formats, such
as schemas, object references, and namespaces.

JSON-LD is a W3C standard providing a way to describe how to interpret a
JSON document as Linked Data by means of a "context".  JSON-LD provides a
powerful solution for representing object references and namespaces in JSON
based on standard web URIs, but is not itself a schema language.  Without a
schema providing a well defined structure, it is difficult to process an
arbitrary JSON-LD document as idiomatic JSON because there are many ways to
express the same data that are logically equivalent but structurally
distinct.

Several schema languages exist for describing and validating JSON data,
such as the Apache Avro data serialization system, however none understand
linked data.  As a result, to fully take advantage of JSON-LD to build the
next generation of linked data applications, one must maintain separate
JSON schema, JSON-LD context, RDF schema, and human documentation, despite
significant overlap of content and obvious need for these documents to stay
synchronized.

Schema Salad is designed to address this gap.  It provides a schema
language and processing rules for describing structured JSON content
permitting URI resolution and strict document validation.  The schema
language supports linked data through annotations that describe the linked
data interpretation of the content, enables generation of JSON-LD context
and RDF schema, and production of RDF triples by applying the JSON-LD
context.  The schema language also provides for robust support of inline
documentation.

## Introduction to v1.0

This is the second version of of the Schema Salad specification.  It is
developed concurrently with v1.0 of the Common Workflow Language for use in
specifying the Common Workflow Language, however Schema Salad is intended to be
useful to a broader audience.  Compared to the draft-1 schema salad
specification, the following changes have been made:

* Use of [mapSubject and mapPredicate](#Identifier_maps) to transform maps to lists of records.
* Resolution of the [domain Specific Language for types](#Domain_Specific_Language_for_types)
* Consolidation of the formal [schema into section 5](#Schema).

## References to Other Specifications

**Javascript Object Notation (JSON)**: http://json.org

**JSON Linked Data (JSON-LD)**: http://json-ld.org

**YAML**: http://yaml.org

**Avro**: https://avro.apache.org/docs/current/spec.html

**Uniform Resource Identifier (URI) Generic Syntax**: https://tools.ietf.org/html/rfc3986)

**Resource Description Framework (RDF)**: http://www.w3.org/RDF/

**UTF-8**: https://www.ietf.org/rfc/rfc2279.txt)

## Scope

This document describes the syntax, data model, algorithms, and schema
language for working with Salad documents.  It is not intended to document
a specific implementation of Salad, however it may serve as a reference for
the behavior of conforming implementations.

## Terminology

The terminology used to describe Salad documents is defined in the Concepts
section of the specification. The terms defined in the following list are
used in building those definitions and in describing the actions of an
Salad implementation:

**may**: Conforming Salad documents and Salad implementations are permitted but
not required to be interpreted as described.

**must**: Conforming Salad documents and Salad implementations are required
to be interpreted as described; otherwise they are in error.

**error**: A violation of the rules of this specification; results are
undefined. Conforming implementations may detect and report an error and may
recover from it.

**fatal error**: A violation of the rules of this specification; results
are undefined. Conforming implementations must not continue to process the
document and may report an error.

**at user option**: Conforming software may or must (depending on the modal verb in
the sentence) behave as described; if it does, it must provide users a means to
enable or disable the behavior described.

# Document model

## Data concepts

An **object** is a data structure equivalent to the "object" type in JSON,
consisting of a unordered set of name/value pairs (referred to here as
**fields**) and where the name is a string and the value is a string, number,
boolean, array, or object.

A **document** is a file containing a serialized object, or an array of
objects.

A **document type** is a class of files that share a common structure and
semantics.

A **document schema** is a formal description of the grammar of a document type.

A **base URI** is a context-dependent URI used to resolve relative references.

An **identifier** is a URI that designates a single document or single
object within a document.

A **vocabulary** is the set of symbolic field names and enumerated symbols defined
by a document schema, where each term maps to absolute URI.

## Syntax

Conforming Salad documents are serialized and loaded using YAML syntax and
UTF-8 text encoding.  Salad documents are written using the JSON-compatible
subset of YAML.  Features of YAML such as headers and type tags that are
not found in the standard JSON data model must not be used in conforming
Salad documents.  It is a fatal error if the document is not valid YAML.

A Salad document must consist only of either a single root object or an
array of objects.

## Document context

### Implied context

The implicit context consists of the vocabulary defined by the schema and
the base URI.  By default, the base URI must be the URI that was used to
load the document.  It may be overridden by an explicit context.

### Explicit context

If a document consists of a root object, this object may contain the
fields `$base`, `$namespaces`, `$schemas`, and `$graph`:

  * `$base`: Must be a string.  Set the base URI for the document used to
    resolve relative references.

  * `$namespaces`: Must be an object with strings as values.  The keys of
    the object are namespace prefixes used in the document; the values of
    the object are the prefix expansions.

  * `$schemas`: Must be an array of strings.  This field may list URI
    references to documents in RDF-XML format which will be queried for RDF
    schema data.  The subjects and predicates described by the RDF schema
    may provide additional semantic context for the document, and may be
    used for validation of prefixed extension fields found in the document.

Other directives beginning with `$` must be ignored.

## Document graph

If a document consists of a single root object, this object may contain the
field `$graph`.  This field must be an array of objects.  If present, this
field holds the primary content of the document.  A document that consists
of array of objects at the root is an implicit graph.

## Document metadata

If a document consists of a single root object, metadata about the
document, such as authorship, may be declared in the root object.

## Document schema

Document preprocessing, link validation and schema validation require a
document schema.  A schema may consist of:

  * At least one record definition object which defines valid fields that
  make up a record type.  Record field definitions include the valid types
  that may be assigned to each field and annotations to indicate fields
  that represent identifiers and links, described below in "Semantic
  Annotations".

  * Any number of enumerated type objects which define a set of finite set of symbols that are
  valid value of the type.

  * Any number of documentation objects which allow in-line documentation of the schema.

The schema for defining a salad schema (the metaschema) is described in
detail in "Schema validation".

### Record field annotations

In a document schema, record field definitions may include the field
`jsonldPredicate`, which may be either a string or object.  Implementations
must use the following document preprocessing of fields by the following
rules:

  * If the value of `jsonldPredicate` is `@id`, the field is an identifier
  field.

  * If the value of `jsonldPredicate` is an object, and contains that
  object contains the field `_type` with the value `@id`, the field is a
  link field.

  * If the value of `jsonldPredicate` is an object, and contains that
  object contains the field `_type` with the value `@vocab`, the field is a
  vocabulary field, which is a subtype of link field.

## Document traversal

To perform document document preprocessing, link validation and schema
validation, the document must be traversed starting from the fields or
array items of the root object or array and recursively visiting each child
item which contains an object or arrays.

# Document preprocessing

After processing the explicit context (if any), document preprocessing
begins.  Starting from the document root, object fields values or array
items which contain objects or arrays are recursively traversed
depth-first.  For each visited object, field names, identifier fields, link
fields, vocabulary fields, and `$import` and `$include` directives must be
processed as described in this section.  The order of traversal of child
nodes within a parent node is undefined.
