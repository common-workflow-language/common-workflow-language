## References to other specifications

**Javascript Object Notation (JSON)**: http://json.org

**JSON Linked Data (JSON-LD)**: http://json-ld.org

**YAML**: http://yaml.org

**Avro**: https://avro.apache.org/docs/current/spec.html

**Uniform Resource Identifier (URI) Generic Syntax**: https://tools.ietf.org/html/rfc3986)

**Internationalized Resource Identifiers (IRIs)**:
https://tools.ietf.org/html/rfc3987

**Portable Operating System Interface (POSIX.1-2008)**: http://pubs.opengroup.org/onlinepubs/9699919799/

**Resource Description Framework (RDF)**: http://www.w3.org/RDF/

## Scope

This document describes CWL syntax, execution, and object model.  It
is not intended to document a CWL specific implementation, however it may
serve as a reference for the behavior of conforming implementations.

## Terminology

The terminology used to describe CWL documents is defined in the
Concepts section of the specification. The terms defined in the
following list are used in building those definitions and in describing the
actions of a CWL implementation:

**may**: Conforming CWL documents and CWL implementations are permitted but
not required to behave as described.

**must**: Conforming CWL documents and CWL implementations are required to behave
as described; otherwise they are in error.

**error**: A violation of the rules of this specification; results are
undefined. Conforming implementations may detect and report an error and may
recover from it.

**fatal error**: A violation of the rules of this specification; results are
undefined. Conforming implementations must not continue to execute the current
process and may report an error.

**at user option**: Conforming software may or must (depending on the modal verb in
the sentence) behave as described; if it does, it must provide users a means to
enable or disable the behavior described.

**deprecated**: Conforming software may implement a behavior for backwards
compatibility.  Portable CWL documents should not rely on deprecated behavior.
Behavior marked as deprecated may be removed entirely from future revisions of
the CWL specification.

# Data model

## Data concepts

An **object** is a data structure equivalent to the "object" type in JSON,
consisting of a unordered set of name/value pairs (referred to here as
**fields**) and where the name is a string and the value is a string, number,
boolean, array, or object.

A **document** is a file containing a serialized object, or an array of objects.

A **process** is a basic unit of computation which accepts input data,
performs some computation, and produces output data. Examples include
CommandLineTools, Workflows, and ExpressionTools.

An **input object** is an object describing the inputs to an invocation of
a process.

An **output object** is an object describing the output resulting from an
invocation of a process.

An **input schema** describes the valid format (required fields, data types)
for an input object.

An **output schema** describes the valid format for an output object.

**Metadata** is information about workflows, tools, or input items.

## Syntax

CWL documents must consist of an object or array of objects represented using
JSON or YAML syntax.  Upon loading, a CWL implementation must apply the
preprocessing steps described in the
[Semantic Annotations for Linked Avro Data (SALAD) Specification](SchemaSalad.html).
An implementation may formally validate the structure of a CWL document using
SALAD schemas located at
https://github.com/common-workflow-language/common-workflow-language/tree/master/v1.0

## Identifiers

If an object contains an `id` field, that is used to uniquely identify the
object in that document.  The value of the `id` field must be unique over the
entire document.  Identifiers may be resolved relative to either the document
base and/or other identifiers following the rules are described in the
[Schema Salad specification](SchemaSalad.html#Identifier_resolution).

An implementation may choose to only honor references to object types for
which the `id` field is explicitly listed in this specification.

## Document preprocessing

An implementation must resolve [$import](SchemaSalad.html#Import) and
[$include](SchemaSalad.html#Import) directives as described in the
[Schema Salad specification](SchemaSalad.html).

Another transformation defined in Schema salad is simplification of data type definitions.
Type `<T>` ending with `?` should be transformed to `[<T>, "null"]`.
Type `<T>` ending with `[]` should be transformed to `{"type": "array", "items": <T>}`

## Extensions and metadata

Input metadata (for example, a lab sample identifier) may be represented within
a tool or workflow using input parameters which are explicitly propagated to
output.  Future versions of this specification may define additional facilities
for working with input/output metadata.

Implementation extensions not required for correct execution (for example,
fields related to GUI presentation) and metadata about the tool or workflow
itself (for example, authorship for use in citations) may be provided as
additional fields on any object.  Such extensions fields must use a namespace
prefix listed in the `$namespaces` section of the document as described in the
[Schema Salad specification](SchemaSalad.html#Explicit_context).

Implementation extensions which modify execution semantics must be [listed in
the `requirements` field](#Requirements_and_hints).

# Execution model

## Execution concepts

A **parameter** is a named symbolic input or output of process, with an
associated datatype or schema.  During execution, values are assigned to
parameters to make the input object or output object used for concrete
process invocation.

A **CommandLineTool** is a process characterized by the execution of a
standalone, non-interactive program which is invoked on some input,
produces output, and then terminates.

A **workflow** is a process characterized by multiple subprocess steps,
where step outputs are connected to the inputs of downstream steps to
form a directed acylic graph, and independent steps may run concurrently.

A **runtime environment** is the actual hardware and software environment when
executing a command line tool.  It includes, but is not limited to, the
hardware architecture, hardware resources, operating system, software runtime
(if applicable, such as the specific Python interpreter or the specific Java
virtual machine), libraries, modules, packages, utilities, and data files
required to run the tool.

A **workflow platform** is a specific hardware and software implementation
capable of interpreting CWL documents and executing the processes specified by
the document.  The responsibilities of the workflow platform may include
scheduling process invocation, setting up the necessary runtime environment,
making input data available, invoking the tool process, and collecting output.

A workflow platform may choose to only implement the Command Line Tool
Description part of the CWL specification.

It is intended that the workflow platform has broad leeway outside of this
specification to optimize use of computing resources and enforce policies
not covered by this specification.  Some areas that are currently out of
scope for CWL specification but may be handled by a specific workflow
platform include:

* Data security and permissions
* Scheduling tool invocations on remote cluster or cloud compute nodes.
* Using virtual machines or operating system containers to manage the runtime
(except as described in [DockerRequirement](CommandLineTool.html#DockerRequirement)).
* Using remote or distributed file systems to manage input and output files.
* Transforming file paths.
* Determining if a process has previously been executed, and if so skipping it
and reusing previous results.
* Pausing, resuming or checkpointing processes or workflows.

Conforming CWL processes must not assume anything about the runtime
environment or workflow platform unless explicitly declared though the use
of [process requirements](#Requirements_and_hints).

## Generic execution process

The generic execution sequence of a CWL process (including workflows and
command line line tools) is as follows.

1. Load, process and validate a CWL document, yielding a process object.
2. Load input object.
3. Validate the input object against the `inputs` schema for the process.
4. Validate process requirements are met.
5. Perform any further setup required by the specific process type.
6. Execute the process.
7. Capture results of process execution into the output object.
8. Validate the output object against the `outputs` schema for the process.
9. Report the output object to the process caller.

## Requirements and hints

A **process requirement** modifies the semantics or runtime
environment of a process.  If an implementation cannot satisfy all
requirements, or a requirement is listed which is not recognized by the
implementation, it is a fatal error and the implementation must not attempt
to run the process, unless overridden at user option.

A **hint** is similar to a requirement; however, it is not an error if an
implementation cannot satisfy all hints.  The implementation may report a
warning if a hint cannot be satisfied.

Requirements are inherited.  A requirement specified in a Workflow applies
to all workflow steps; a requirement specified on a workflow step will
apply to the process implementation of that step and any of its substeps.

If the same process requirement appears at different levels of the
workflow, the most specific instance of the requirement is used, that is,
an entry in `requirements` on a process implementation such as
CommandLineTool will take precedence over an entry in `requirements`
specified in a workflow step, and an entry in `requirements` on a workflow
step takes precedence over the workflow.  Entries in `hints` are resolved
the same way.

Requirements override hints.  If a process implementation provides a
process requirement in `hints` which is also provided in `requirements` by
an enclosing workflow or workflow step, the enclosing `requirements` takes
precedence.

## Parameter references

Parameter references are denoted by the syntax `$(...)` and may be used in any
field permitting the pseudo-type `Expression`, as specified by this document.
Conforming implementations must support parameter references.  Parameter
references use the following subset of
[Javascript/ECMAScript 5.1](http://www.ecma-international.org/ecma-262/5.1/)
syntax, but they are designed to not require a Javascript engine for evaluation.

In the following BNF grammar, character classes, and grammar rules are denoted
in '{}', '-' denotes exclusion from a character class, '(())' denotes grouping,
'|' denotes alternates, trailing '*' denotes zero or more repeats, '+' denote
one or more repeats, '/' escapes these special characters, and all other
characters are literal values.

<p>
<table class="table">
<tr><td>symbol::             </td><td>{Unicode alphanumeric}+</td></tr>
<tr><td>singleq::            </td><td>[' (( {character - '} | \' ))* ']</td></tr>
<tr><td>doubleq::            </td><td>[" (( {character - "} | \" ))* "]</td></tr>
<tr><td>index::              </td><td>[ {decimal digit}+ ]</td></tr>
<tr><td>segment::            </td><td>. {symbol} | {singleq} | {doubleq} | {index}</td></tr>
<tr><td>parameter reference::</td><td>$( {symbol} {segment}*)</td></tr>
</table>
</p>

Use the following algorithm to resolve a parameter reference:

  1. Match the leading symbol as the key
  2. Look up the key in the parameter context (described below) to get the current value.
     It is an error if the key is not found in the parameter context.
  3. If there are no subsequent segments, terminate and return current value
  4. Else, match the next segment
  5. Extract the symbol, string, or index from the segment as the key
  6. Look up the key in current value and assign as new current value.  If
     the key is a symbol or string, the current value must be an object.
     If the key is an index, the current value must be an array or string.
     It is an error if the key does not match the required type, or the key is not found or out
     of range.
  7. Repeat steps 3-6

The root namespace is the parameter context.  The following parameters must
be provided:

  * `inputs`: The input object to the current Process.
  * `self`: A context-specific value.  The contextual values for 'self' are
    documented for specific fields elsewhere in this specification.  If
    a contextual value of 'self' is not documented for a field, it
    must be 'null'.
  * `runtime`: An object containing configuration details.  Specific to the
    process type.  An implementation may provide
    opaque strings for any or all fields of `runtime`.  These must be
    filled in by the platform after processing the Tool but before actual
    execution.  Parameter references and expressions may only use the
    literal string value of the field and must not perform computation on
    the contents, except where noted otherwise.

If the value of a field has no leading or trailing non-whitespace
characters around a parameter reference, the effective value of the field
becomes the value of the referenced parameter, preserving the return type.

If the value of a field has non-whitespace leading or trailing characters
around a parameter reference, it is subject to string interpolation.  The
effective value of the field is a string containing the leading characters,
followed by the string value of the parameter reference, followed by the
trailing characters.  The string value of the parameter reference is its
textual JSON representation with the following rules:

  * Leading and trailing quotes are stripped from strings
  * Objects entries are sorted by key

Multiple parameter references may appear in a single field.  This case
must be treated as a string interpolation.  After interpolating the first
parameter reference, interpolation must be recursively applied to the
trailing characters to yield the final string value.

## Expressions

An expression is a fragment of [Javascript/ECMAScript
5.1](http://www.ecma-international.org/ecma-262/5.1/) code evaluated by the
workflow platform to affect the inputs, outputs, or
behavior of a process.  In the generic execution sequence, expressions may
be evaluated during step 5 (process setup), step 6 (execute process),
and/or step 7 (capture output).  Expressions are distinct from regular
processes in that they are intended to modify the behavior of the workflow
itself rather than perform the primary work of the workflow.

To declare the use of expressions, the document must include the process
requirement `InlineJavascriptRequirement`.  Expressions may be used in any
field permitting the pseudo-type `Expression`, as specified by this
document.

Expressions are denoted by the syntax `$(...)` or `${...}`.  A code
fragment wrapped in the `$(...)` syntax must be evaluated as a
[ECMAScript expression](http://www.ecma-international.org/ecma-262/5.1/#sec-11).  A
code fragment wrapped in the `${...}` syntax must be evaluated as a
[EMACScript function body](http://www.ecma-international.org/ecma-262/5.1/#sec-13)
for an anonymous, zero-argument function.  Expressions must return a valid JSON
data type: one of null, string, number, boolean, array, object. Other return
values must result in a `permanentFailure`. Implementations must permit any
syntactically valid Javascript and account for nesting of parenthesis or braces
and that strings that may contain parenthesis or braces when scanning for
expressions.

The runtime must include any code defined in the ["expressionLib" field of
InlineJavascriptRequirement](#InlineJavascriptRequirement) prior to
executing the actual expression.

Before executing the expression, the runtime must initialize as global
variables the fields of the parameter context described above.

The effective value of the field after expression evaluation follows the
same rules as parameter references discussed above.  Multiple expressions
may appear in a single field.

Expressions must be evaluated in an isolated context (a "sandbox") which
permits no side effects to leak outside the context.  Expressions also must
be evaluated in [Javascript strict mode](http://www.ecma-international.org/ecma-262/5.1/#sec-4.2.2).

The order in which expressions are evaluated is undefined except where
otherwise noted in this document.

An implementation may choose to implement parameter references by
evaluating as a Javascript expression.  The results of evaluating
parameter references must be identical whether implemented by Javascript
evaluation or some other means.

Implementations may apply other limits, such as process isolation, timeouts,
and operating system containers/jails to minimize the security risks associated
with running untrusted code embedded in a CWL document.

Exceptions thrown from an exception must result in a `permanentFailure` of the
process.

## Executing CWL documents as scripts

By convention, a CWL document may begin with `#!/usr/bin/env cwl-runner`
and be marked as executable (the POSIX "+x" permission bits) to enable it
to be executed directly.  A workflow platform may support this mode of
operation; if so, it must provide `cwl-runner` as an alias for the
platform's CWL implementation.

A CWL input object document may similarly begin with `#!/usr/bin/env
cwl-runner` and be marked as executable.  In this case, the input object
must include the field `cwl:tool` supplying an IRI to the default CWL
document that should be executed using the fields of the input object as
input parameters.

## Discovering CWL documents on a local filesystem

To discover CWL documents look in the following locations:

`/usr/share/commonwl/`

`/usr/local/share/commonwl/`

`$XDG_DATA_HOME/commonwl/` (usually `$HOME/.local/share/commonwl`)

`$XDF_DATA_HOME` is from the [XDG Base Directory
Specification](http://standards.freedesktop.org/basedir-spec/basedir-spec-0.6.html)
