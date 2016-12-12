Schema Salad
------------

Salad is a schema language for describing JSON or YAML structured linked data
documents.  Salad is based originally on JSON-LD_ and the Apache Avro_ data
serialization system.

Salad schema describes rules for preprocessing, structural validation, and link
checking for documents described by a Salad schema. Salad features for rich
data modeling such as inheritance, template specialization, object identifiers,
object references, documentation generation, and transformation to RDF_. Salad
provides a bridge between document and record oriented data modeling and the
Semantic Web.

Usage
-----

::

   $ pip install schema_salad
   $ schema-salad-tool
   usage: schema-salad-tool [-h] [--rdf-serializer RDF_SERIALIZER]
                         [--print-jsonld-context | --print-doc | --print-rdfs | --print-avro | --print-rdf | --print-pre | --print-index | --print-metadata | --version]
                         [--strict | --non-strict]
                         [--verbose | --quiet | --debug]
                         schema [document]
   $ python
   >>> import schema_salad

Documentation
-------------

See the specification_ and the metaschema_ (salad schema for itself).  For an
example application of Schema Salad see the Common Workflow Language_.

Rationale
---------

The JSON data model is an popular way to represent structured data.  It is
attractive because of it's relative simplicity and is a natural fit with the
standard types of many programming languages.  However, this simplicity comes
at the cost that basic JSON lacks expressive features useful for working with
complex data structures and document formats, such as schemas, object
references, and namespaces.

JSON-LD is a W3C standard providing a way to describe how to interpret a JSON
document as Linked Data by means of a "context".  JSON-LD provides a powerful
solution for representing object references and namespaces in JSON based on
standard web URIs, but is not itself a schema language.  Without a schema
providing a well defined structure, it is difficult to process an arbitrary
JSON-LD document as idiomatic JSON because there are many ways to express the
same data that are logically equivalent but structurally distinct.

Several schema languages exist for describing and validating JSON data, such as
JSON Schema and Apache Avro data serialization system, however none
understand linked data.  As a result, to fully take advantage of JSON-LD to
build the next generation of linked data applications, one must maintain
separate JSON schema, JSON-LD context, RDF schema, and human documentation,
despite significant overlap of content and obvious need for these documents to
stay synchronized.

Schema Salad is designed to address this gap.  It provides a schema language
and processing rules for describing structured JSON content permitting URI
resolution and strict document validation.  The schema language supports linked
data through annotations that describe the linked data interpretation of the
content, enables generation of JSON-LD context and RDF schema, and production
of RDF triples by applying the JSON-LD context.  The schema language also
provides for robust support of inline documentation.

.. _JSON-LD: http://json-ld.org
.. _Avro: http://avro.apache.org
.. _metaschema: https://github.com/common-workflow-language/schema_salad/blob/master/schema_salad/metaschema/metaschema.yml
.. _specification: http://www.commonwl.org/v1.0/SchemaSalad.html
.. _Language: https://github.com/common-workflow-language/common-workflow-language/blob/master/v1.0/CommandLineTool.yml
.. _RDF: https://www.w3.org/RDF/
