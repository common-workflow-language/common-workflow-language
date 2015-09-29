Common Workflow Language Tool Description, Draft 1
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

The tool description document and job order document are written in
[YAML](http://www.yaml.org/).  Note that YAML type system is very similar to
[JSON](http://json.org), and all JSON documents are also valid YAML documents;
so you may choose to use only the JSON-compatible subset of YAML syntax (this
is the case for all the examples in this specification).  The formal schema for
the tool description document is written using [JSON Schema draft v4](http://json-schema.org)
and available at
<https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/tool.json>

Tool description documents must include a "schema" field with a URL
for the formal tool schema. For example, a tool that follows the
draft-1 schema described here must have a tool description document
that includes the following "schema" field:

```json
{
  "schema": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/tool.json"
}
```

## References, Mixins, Imports, and Expressions

This section describes certain fields that are evaluated during the
loading and interpretation of the tool description document.

### References

Use a [JSON reference](https://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03)
to indicate that the field value should be obtained by following a
[JSON pointer](https://tools.ietf.org/html/draft-ietf-appsawg-json-pointer-04)
to another field.

A field in the tool description document may reference either another
field within the tool description document, or a field in the job
order document.

A reference is formatted as a JSON object with one field, named either
"$ref" or "$job".  The value of this field is a JSON pointer to the
field being referenced.  If the field name is "$ref", the JSON pointer
is interpreted relative to the tool description document; if "$job",
it is interpreted relative to the job order document.

#### Examples

- In this example, "item1" references the value of "item2" within the same
document:

doc0.json:
```json
{
  "item1": 12,
  "item2": {"$ref": "#item1"}
}
```

After resolving the reference:

```json
{
  "item1": 12,
  "item2": 12
}
```

- In this example, "item1" in "doc1.json" references to the value of "item2" in
"doc2.json":

doc1.json:
```json
{
  "item1": {"$ref": "doc2.json#item2"}
}
```

doc2.json:
```json
{
  "item2": 12
}
```

After resolving the reference, doc1.json has the following contents:

```json
{
  "item1": 12
}
```

- In this example, use "$job" to refer to the job order document.

doc1.json:
```json
{
  "item1": {"$job": "#/inputs/item1"}
}
```

job1.json:
```json
{
  "inputs": {
    "item1": 13
  }
}
```

After resolving the reference, doc1.json has the following contents:

doc1.json:
```json
{
  "item1": 13
}
```

### Mixins

Use a *mixin* field, specified with the field name "$mixin", to
indicate that each field of a *source* object should be inserted into
the *destination* object.  The object containing the "$mixin" field is
the destination object.  The "$mixin" field specifies a [JSON
Pointer](https://tools.ietf.org/html/draft-ietf-appsawg-json-pointer-04)
to a source object.  It is an error if the source is not a json
object.  If the destination object already contains a field that is
found on the source object, the value will remain unchanged on the
destination object.  Mixins can be used anywhere in the document and
are evaluated on document load.

#### Example

doc1.json:
```json
{
  "item1": 11,
  "$mixin": "doc2.json#"
}
```

doc2.json:
```json
{
  "item1": 10,
  "item2": 12
}
```

After evaluating the mixin, doc1.json has the following contents:

```json
{
  "item1": 11,
  "item2": 12
}
```

### Imports

An *import*, identified by an object with a single "$import" field, specifies a
URL of a file to be loaded.  Relative URL paths are resolved with respect to
the location of the tool description document.  The "$import" object is
replaced by the a string with the file contents.

hello.txt:
```
hello world
```

doc1.json:
```json
{
  "item1": {"$import": "hello.txt"}
}
```

After evaluating the import:

```json
{
  "item1": "hello world"
}
```

### Expressions

An *expression*, identified by an object with a single "$expr" field,
contains a string of [Javascript/ECMAScript
5.1](http://www.ecma-international.org/ecma-262/5.1/) code.  When the
tool description document is loaded, this code is evaluated and its
output is substituted for the "$expr" object.

If the "$expr" value string is enclosed in braces ("{" and "}") then
it will be interpreted as a [function
body](http://www.ecma-international.org/ecma-262/5.1/#sec-13) for an
anonymous, zero-argument function, and the value of "$expr" will be
the value returned when this function is executed.  Otherwise, the
"$expr" code will be interpreted as a [Javascript
expression](http://www.ecma-international.org/ecma-262/5.1/#sec-11),
and the value of "$expr" will be the result of evaluating the
expression.

Before executing the expression, the runtime shall initialize a
JavaScript variable "$job" containing a copy of the validated contents
of the job order document.  This variable will be available in the
expression's global namespace when the expression is evaluated.

The runtime shall also include any code defined in the ["expressionlib" section
of "requirements"](#expression-library).

Expressions must be evaluated in an isolated context (a "sandbox")
which permits no side effects to leak outside the context.
Expressions also must be evaluated in
[Javascript strict mode](http://www.ecma-international.org/ecma-262/5.1/#sec-4.2.2).

The order in which expressions are evaluated is undefined.

Implementations may apply other limits, such as process isolation, timeouts,
and operating system containers/jails to minimize the security risks associated
with running untrusted code embedded in a tool description document.

#### Examples

- Assume the following job order document in "$job"

```json
{
  "inputs": {
    "i": 3
  }
}
```

The following expression can access the job order:

```json
{
  "item": {"$expr": "$job.inputs.i + 2"}
}
```

This evaluates to:

```json
{
  "item": 5
}
```

- The job order document can include array values:

```json
{
  "inputs": {
    "i": [1, 2, 3]
  }
}
```

Example of an expression which defines an anonymous function:

```json
{
  "item": {"$expr": "{ var a; var b = $job.inputs.i; for (a = 0; a < b.length; a += 1) { b[a] += 2; } return b; }"}
}
```

Evaluates to:

```json
{
  "item": [3, 4, 5]
}
```

## Input schema

The input schema is stored in the "inputs" field of the tool document.  The value
of "inputs" is a formal description of the format of the input record.  The
schema language formally defined at
<https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/metaschema.json>

The input schema is based on [JSON Schema draft v4](http://json-schema.org),
with the following differences:

- The
  ["$schema" keyword](http://json-schema.org/latest/json-schema-core.html#anchor22)
  is unnecessary and will be ignored.  The input schema is always validated
  against the "metaschema" linked above.

- An additional
[primitive type](http://json-schema.org/latest/json-schema-core.html#anchor8)
of "file".  When `{"type": "file"}` is encountered, it specifies an
input that will be validated against the `/definitions/file` stanza
of the metaschema. (Specifically, it will be treated as though the
input schema type included `{"$mixin":
"https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/metaschema.json#/definitions/file"}`
and the value of "type" were changed to "object".) See [file records](#file-records) below.

- The addition of "adapter" sections, discussed below.

Consult
[JSON Schema Core](http://json-schema.org/latest/json-schema-core.html),
[JSON Schema Validation](http://json-schema.org/latest/json-schema-validation.html),
and [JSON Schema examples](http://json-schema.org/examples.html) for detailed
information about schema structure, keywords, and validation options.

Any object in the schema where the "type" keyword is meaningful may contain a
field named "adapter" containing an [Adapter record](#adapter-record).  The
adapter describes how the value from the job order record should be translated
into command line argument(s) and is described below.  If no adapter section is
present, nothing will be added to the command line for that field, unless it is
referenced some other way.

The input schema top level must be `{"type": "object"}`.

### File records

File records have five fields.

**Required**

- "path" (type: string) An absolute path to the file on the local
  file system.

**Optional**

- "size" (type: integer)  File size in bytes.

- "checksum" (type: string)  A hash of the file contents.  (Format is
  currently unspecified; see [TODO](#TODO).)

- "metadata" (type: record)  A record containing an arbitrary JSON
  structure.  Currently there is no explicit behavior related to the "metadata"
  section, but references or expressions may be used to propagate metadata from
  the input record to the [output record](#output-adapter-record).

- "secondaryFiles" (type: array of file records)  A list of files
  which are dependent on this file, or this file depends on, such as indexes or
  external references.

## Command line adapter

The command line adapter record is stored in the "adapter" field of
the tool document.  This record consists of the following fields:

**Required**

- "baseCmd" (type: string, expression, or reference or array of such) The program to
  execute, as well as any command line arguments which must come before all
  others (such as a subcommand)

- "args" (type: array) A list of adapter records.  See below.

**Optional**

- "stdin" (type: string, expression, or reference)  A path to a file to be piped to the
  standard input stream of the tool process.

- "stdout" (type: string, expression, or reference)  The name of a
  file, relative to the designated output directory, to which the standard
  output stream of the tool process will be directed.

### Adapter record

If the adapter record is listed in the input schema, "value" is set to the
corresponding value for that input join the job order document.  For adapter
records listed in "args", "value" must be provided or it is an error.  The
"value" field may be a [reference](#references) or [expression](#expressions).
The adapter behavior in building the command line depends on the data type of
the value.  Note: in the event of a mismatch between the data type specified in
the schema and the data type of the actual value (this can occur when applying
expressions), use the data type of the actual value to select the appropriate
behavior:

- array: each value of the array will be added as separate command line
entries, unless "itemSeparator" is specified (see below).

- boolean: Indicates that this argument represents a boolean
  command-line flag. If true, indicates that the value in "prefix"
  (see below) should be added to the command line.  If false, nothing
  is added.

- file: Add the "path" field of the file object to the command line.  Note that
  the actual path used to invoke the tool may be different due to path
  rewriting.

- null: nothing is added to the command line.

- number: Convert to decimal text string representation and add an entry to the
  the command line.

- object: the value of "prefix" is added to the command line.  The contents of
  the object may be serialized with a nested adapter, and appended to "prefix."

- string: Added unchanged to the command line.

The following optional fields modify the above behavior:

- "prefix" (type: string, default: none) A string to prepend to the field value when
  constructing the command line.

- "order" (type: integer, default: 1000000) The sort order, relative to other
  command line arguments at the same adapter nesting depth.  If order is
  missing, the large default should cause arguments to be generally placed at
  to the end.

- "separator" (type: string, default: none) The separator between the prefix
  and the value.  If separator not defined, or the value of separator is a
  single space, the prefix and field value will be separate entries in the
  command line arguments array; otherwise the command line entry will be a
  single entry which is the concatenation of prefix+separator+value.

- "itemSeparator" (type: string, default: none) If the field value is an array,
  join each value in the array into a single string separated by the value of
  itemSeparator.

- "streamable" (type: boolean, default: false) For file types only.  Provided as a hint to the
  workflow infrastructure for how the file will be accessed.  Indicates that
  the tool reads the file linearly from start to finish with no seeking or
  random access.

### Example

Given the following tool input schema:

```json
{
  "inputs": {
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
        "maximum": 100
      },
      "param2": {
        "type": "array",
        "items": {"type": "string"},
        "adapter": {
          "order": 1,
          "separator": " ",
          "prefix": "--list",
          "itemSeparator": ","
        }
      }
    }
  },
  "adapter": {
    "baseCmd": "example",
    "args": [
    {
      "prefix": "-p",
      "value": {"$ref": "#/inputs/param1"},
      "order": 1
    }
    ]
  }
}
```

The inputs record of job order consists of three fields: "input1", "param1", and
"param2".  Of those, "input1" and "param1" are required and "param2" is
optional (it may be missing from the job order record).

Given the following job order:

```json
{
  "inputs": {
    "input1": {
      "path": "/foo/bar.txt"
    },
    "param1": 44,
    "param2": ["a", "b", "c"]
  }
}
```

The input schema adapters are applied to build the following command line
fragment.

```json
["example", "-p44", "--list", "a,b,c", "/foo/bar.txt"]
```

Note that parameters are sorted based on the order field, with lower sort
orders preceeding higher sort orders.  Here, `{"order: 2"}` in the "input1"
adapter causes it to be sorted after "param1" and "param2" `{"order: 1"}`.
Where parameters have the same sort order weight, command line parameters in
the "args" field sort before input schema adapters, in the order that they are
declared in "args".  Where input schema adapters have the same sort order
weight, they are sorted based on the lexical ordering of the field name.

## Tool requirements

The tool requirements is stored in the "requirements" field of the tool
document.  Tool requirements describe the hardware and software prerequisites
for running the tool.

There are three fields, "environment", "resources", and "expressionlib".

### Environment

The "environment" field of "requirements" describes the runtime environment.
It has a single field, "container".

#### Container

The "container" field of "environment" specifies a container image that
encapsulates the runtime environment.  There are three fields:

- "type" (type: string) Type of container.  Currently only supports "docker".

- "uri" (type: string) A Docker image name suitable for use with "docker pull".

- "imageId" (type: string) The Docker image name that will be used to for "docker run".

### Resources

The "resources" field of "requirements" describes hardware and operating system
resources.  It has two fields, which may contain expressions
or references (this permits calculating the resource requirements based on the
size of the input).

- "cpu" (type: integer) Minimum number of CPU cores

- "mem" (type: integer) Minimum RAM, in megabytes

## Expression library

The expression library ("expressionlib") is an array consisting of fragments of
Javascript which will be included before evaluating an expression.  This allows
defining commonly-used functions in a single place.  Each item of the
expressionlib array must be a string or [file import](#imports).  Code
fragments are included in the order they are listed.

### Example

The following example includes the [underscore.js library](http://underscorejs.org/),
then defines a function "t" as a convenience method for the underscore.js
template feature.

```json
{
  "requirements": {
    "expressionlib": [
      { "$import": "underscore.js" },
      "var t = function(s) { return _.template(s)({'$job': $job}); };"
    ]
  }
}
```

## Output schema

The output schema is stored in the "outputs" field of the root object.  The
value of "outputs" is a template to build the output record.  The output schema
uses the same format as the input schema, defined at
<https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/metaschema.json>

The output schema top level must be `{"type": "object"}`

### Output adapter record

Any object in the schema where the "type" keyword is meaningful may contain an
"adapter" object.  The adapter describes how output data from the tool execution
should be used to build the output record.

If no adapter section is present, the field will not be added to the output record.

The output schema recognizes two fields in the "adapter" record:

- "glob" (type: string) Find files that match a POSIX "glob" pattern, relative
  to the designated output directory.  If the field type in the schema is
  "array", the output record will contain a list of all files matching the pattern.  If the field
  type in the schema is "file", one matching file from the array will be chosen (which one
  is chosen is undefined).

- "value" (type: any primitive type, expression or reference) A value to be
  added to the output document under the output schema field.

After the tool process finishes, if the directory contains a file called "result.cwl.json",
no output adapters will be used and the content of that file must be the output record.

#### Example

```json
{
  "outputs": {
    "type": "object",
    "properties": {
      "product": {
        "type": "array",
        "items": {"type":"file"},
        "adapter": {
          "glob": "*.txt"
        }
      }
    }
  }
}
```

If the designated output directory contains:

```
alice.txt   bob.txt   carol.bin
```

Then building the output record based on the above schema will produce:

```json
{
  "outputs": {
    "product": [
      { "path": "alice.txt" },
      { "path": "bob.txt" }
    ]
  }
}
```

## Tool metadata

Tool metadata fields are not used directly in the execution of the tool, but
provide additional information about the tool document and the underlying tool.

### Document author

The "documentAuthor" field of the root document lists the authors of the tool
description document.  May be a string or array of strings.

### Document description

The "documentDescription" field of the root document is a human-readable
description of the tool, its purpose, and usage.

### Software description and release

The "softwareDescription" and "softwareRelase" fields of the root document
lists are currently unspecified.  See [TODO](#TODO).

# TODO

(Items remaining for discussion. May be addressed in this draft, or in a later draft)

* Success/fail field in the output record

* Use [Avro](https://avro.apache.org/docs/current/spec.html) with additional
  validation fields to describe input schema instead of json-schema.

* <http://json-ld.org> context.

* Adapter flag to indicate input file should be linked or copied to the designated output
  directory before executing tool.  Needed to support tools that either want to
  write files alongside existing files, or modify files in place (update a
  copy.)

* Use linked data ontology such as EDAM for classification of tool function, file
  types.

* Use standardized names for file checksum algorithm e.g. <https://www.iana.org/assignments/hash-function-text-names/hash-function-text-names.xhtml>

* Use linked data for specifying authors:

```jsonld
{
  "@context": "http://xmlns.com/foaf/context",
  "@id" : "http://orcid.org/0000-0002-1825-0097",
  "name": "John Smith",
  "email": "j.smith@example.com"
}
```

(The `@id` SHOULD be an [ORCID](http://orcid.org/) identifier, but MAY be any
other [Web-ID](http://www.w3.org/TR/webid/))

* Use linked data for specifying project metadata:

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
