SALAD is Semantic Annotations for Linked Avro Data.
---------------------------------------------------

Salad is a schema language for describing structured linked data documents in
JSON or YAML documents.  A Salad schema provides rules for preprocessing,
structural validation, and link checking for documents described by a Salad
schema.  Salad builds on JSON-LD and the Apache Avro data serialization system,
and extends Avro with features for rich data modeling such as inheritance,
template specialization, object identifiers, and object references.  Salad was
developed to provide a bridge between the record oriented data modeling
supported by Apache Avro and the Semantic Web.

Rationale
---------

The JSON data model is an extremely popular way to represent structured data.
It is attractive because of it's relative simplicity and is a natural fit with
the standard types of many programming languages.  However, this simplicity
means that basic JSON lacks expressive features useful for working with complex
data structures and document formats, such as schemas, object references, and
namespaces.

JSON-LD is a W3C standard providing a way to describe how to interpret a JSON
document as Linked Data by means of a "context".  JSON-LD provides a powerful
solution for representing object references and namespaces in JSON based on
standard web URIs, but is not itself a schema language.  Without a schema
providing a well defined structure, it is difficult to process an arbitrary
JSON-LD document as idiomatic JSON because there are many ways to express the
same data that are logically equivalent but structurally distinct.

Several schema languages exist for describing and validating JSON data, such as
the Apache Avro data serialization system, however none understand linked data.
As a result, to fully take advantage of JSON-LD to build the next generation of
linked data applications, one must maintain separate JSON schema, JSON-LD
context, RDF schema, and human documentation, despite significant overlap of
content and obvious need for these documents to stay synchronized.

Schema Salad is designed to address this gap.  It provides a schema language
and processing rules for describing structured JSON content permitting URI
resolution and strict document validation.  The schema language supports linked
data through annotations that describe the linked data interpretation of the
content, enables generation of JSON-LD context and RDF schema, and production
of RDF triples by applying the JSON-LD context.  The schema language also
provides for robust support of inline documentation.

Learn more
----------

Please note that Salad is still under development.  Salad is specified by the
metaschema_

.. _metaschema: schema_salad/metaschema.yml
