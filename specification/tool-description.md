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

In this specification, a *record* refers to a data structure consisting of a
unordered set of key-value pairs (referred to here as *fields*), where the keys
are unique strings.  This is functionally equivalent to a JSON "object", python
"dict", or the "hash" or "map" datatypes available in most programming
language.  A *document* is a file containing a serialized record.

The *tool description document* consists of five major parts: the input schema,
the output schema, the command line adapter, tool requirements, and tool
metadata.  The exact syntax and semantics is discussed below in [Syntax](#Syntax).

- The *input schema* formally describes the permissible fields and datatypes of
  the field values that make up input record.  Input fields follow the JSON
  data model, and may consist of string, number, boolean, object, or array
  values.  Files are represented as an object with a string field that is the
  locally-available path to the file.

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

The *runtime environment* refers to the hardware architecture, hardware
resources, operating system, software runtime (if applicable, such as the
Python interpreter or the JVM), along with libraries, modules, packages,
utilities, and data files required to run the tool.

Tools are executed by the *workflow infrastructure*.  The workflow
infrastructure is the underlying platform responsible for interpreting the tool
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

## Assumptions and restrictions

1. Tools run in a POSIX environment.

2. Tools must be non-interactive, command line programs.  Tools must not
   require any kind of console, GUI, or web based user interaction in order to
   start and run to completion.

3. Tool input comes from the command line, the standard input stream, by
   reading files, or by accessing network resources.

4. Tools only read files or directories which are listed in the input record,
   or are part of an explicitly declared runtime environment.

5. Tool output is emitted via the standard output stream, by writing files, or
   by accessing a network resource.

6. Tool input files are read-only.  Tools do not modify existing files, only create
   new ones.

7. Tools only write files to a designated output directory or designated
   scratch space.

8. Tool may be multithreaded or spawn child processes, however when the
   original tool process exits, the tool is considered finished.

9. Tools do not access hardware devices.

# Syntax

The tool description document and job order document are written in
[JSON](http://json.org) format.  The formal schema for the tool description
document is written using [JSON Schema draft v4](http://json-schema.org) and available
at
<https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/tool.json>

Tool description documents must include a "schema" field with the following
URL indicate it follows the draft 1 format:

```json
{
  "schema": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/tool.json"
}
```

## References, Mixins and Expressions

Where noted, certain fields are evaluated during the loading and interpretation
of the tool description document.

### References

Use [JSON Reference](https://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03)
to indicate that the field value should be obtained by following a
[JSON Pointer](https://tools.ietf.org/html/draft-ietf-appsawg-json-pointer-04)
to another field.  A reference is represented as a json object with a field
"$ref" with a string value which is interpreted as the pointer to the desired
value.

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

After resolving the reference doc1.json has the following contents:

```json
{
  "item1": 12
}
```

### Mixins

Use the "$mixin" field to indicate that each field of a *source* object should
be inserted into the *destination* object.  The object containing the "$mixin"
field is the destination object.  The "$mixin" field specifies a
[JSON Pointer](https://tools.ietf.org/html/draft-ietf-appsawg-json-pointer-04)
to a source object.  It is an error if the source is not a json object.  If the
destination object already contains a field that is found on the source object,
the value will remain unchanged on the destination object.

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
  "item1": 10
  "item2": 12
}
```

After evaluating the mixin doc1.json has the following contents:

```json
{
  "item1": 11,
  "item2": 12
}
```

### Expressions

An expression is a code block which will be executed to yield a result which is
substituted in place of the "$expr" object.  An expression is represented as a
json object with a single field "$expr" where the "$expr" field is a string
containing a
[Javascript/ECMAScript 5.1](http://www.ecma-international.org/ecma-262/5.1/)
expression or code block.

If the "$expr" value string does not start with "{" and end with "}" the code
must be interpreted as a
[Javascript expression](http://www.ecma-international.org/ecma-262/5.1/#sec-11).
The value of "$expr" is the result of evaluating the expression.

If the "$expr" value string starts with "{" and ends with "}" the code must be
interpreted as a
[function body](http://www.ecma-international.org/ecma-262/5.1/#sec-13) for an
anonymous, zero-argument function.  The value of "$expr" will be the return
value of the function.

Before executing the expression, the runtime shall initialize a global variable
"$job" which contains a copy of the validated contents of the job order document.

Expressions must evaluate in an isolated context permitting no side effects
outside of the context.  Expressions also must be evaluated in
[Javascript strict mode](http://www.ecma-international.org/ecma-262/5.1/#sec-4.2.2).
The order of evaluation of expressions within a document is undefined.
Implementations may apply other limits, such as process isolation and timeouts
to minimize the security risks associated with running untrusted code embedded
in a tool description document.

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

Expressions can include code blocks:

```json
{
  "item": {"$expr": "{ var a; var b = $job.inputs.i; for (a = 0; a < b.length; a += 1) { b[a] += 2; } return b; }"}
}
```

Evaluates to:

```json
{
  "item1": [3, 4, 5]
}
```

## Input schema

The input schema is stored in the "inputs" field of the root object.  The value
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
of "file".  When `{"type": "file"}` is encountered, it should be treated as
`{"$mixin":
"https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/draft-1/schemas/metaschema.json#/definitions/file"}`
and the value of "type" changed to "object".

- The addition of "adapter" sections, discussed below.

Consult
[JSON Schema Core](http://json-schema.org/latest/json-schema-core.html),
[JSON Schema Validation](http://json-schema.org/latest/json-schema-validation.html),
and [JSON Schema examples](http://json-schema.org/examples.html) for detailed
information about schema structure, keywords, and validation options.

The input schema top level must be `{"type": "object"}`

### Adapters

Any object in the schema where the "type" keyword is meaningful may contain an
"adapter" object.  The adapter describes how the concrete value from the job
order record should be translated into command line argument(s).

If no adapter section is present, nothing will be added to the command line for
that field.

The adapter behavior in building the command line depends on the field type
from the job order record, modified by the options listed below:

- array: each value of the array will be added as separate command line
entries, unless "itemSeparator" is specified (see below).

- boolean: Assume command line flag.  If true, indicates that the value in
  "prefix" should be added to the command line.  If false, nothing is added.

- file: Add the "path" field of the file object to the command line.  Note that
  the actual path used to invoke the tool may be different due to path
  rewriting.

- null: nothing is added to the command line.

- number: Convert to decimal text string representation and add an entry to the
  the command line.

- object: the value of "prefix" is added to the command line.  The contents of
  the object may be added with a nested adapter.

- string: Added unchanged to the command line.

The following optional fields modify the above behavior:

- "prefix" (type: string, default: none) A string to prefix to the field value when
  constructing the command line.

- "order" (type: integer, default: 0) The sort order, relative to other command
  line arguments at the same adapter nesting depth.

- "separator" (type: string, default: none) The separator beween the prefix and
  the value.  If the value of separator is a single space, the prefix and field
  value will be separate entries in the command line arguments array; otherwise
  the command line entry will be a single entry which is the concatination of
  prefix+separator+value.

- "itemSeparator" (type: string, default: none) If the field value is an array,
  join each value in the array into a single string separated by the value of
  itemSeparator.

- "streamable" (type: boolean) For file types only.  Provided as a hint to the
  workflow infrastructure for how the file will be accessed.  Indicates that
  the tool reads the file linearly from start to finish with no seeking or
  random access.

### Example

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


# Command line generation algorithm

TBD.
