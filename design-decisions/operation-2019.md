# Abstract Operations (2019)

## Abstract

This is a documentation of the decisions made in the design of _abstract operations_ outlined in 
[issue #337](https://github.com/common-workflow-language/common-workflow-language/issues/337)
For the specification of the feature please see that issue and the CWL specifications document.

## Motivation

**Use case 1:** While writing or modifying a CWL workflow, 
sometimes a `CommandLineTool` or `Workflow` does not yet exist for a desired 
step, while the rest of the workflow steps has existing tools to use.

**Use case 2:** Often there are multiple implementations that can perform a desired functionality, but they may 
have slight differences in their command line arguments or file requirements.

**Use case 3:** Workflows from non-CWL workflow systems (e.g. KNIME) can in theory be 
expressed in CWL, even if some of the steps can't have a CWL-equivalent implementation 
(e.g. not command-line based); these can still benefit from being expressed as CWL for 
describing the workflow as a "boxes and arrows" outline with accompanying semantic annotations.

**Use case 4:** A workflow repository or designer wants to visualize a workflow that is not 
yet fully implemented.

**Use case 5:** A user wants to draft the next steps of their workflows, but also keep running 
the initial half.


Typed programming languages frequently have the concept of an 
[interface](https://en.wikipedia.org/wiki/Interface_(Java)) or 
[abstract type](https://en.wikipedia.org/wiki/Abstract_type) which defines the type 
signature of inputs and outputs, but does not embed its executable implementation.


## Current situation (CWL 1.1)


For **use case 1**, current CWL implementations of `cwltool` will fail validation of a `CommandLineTool` without 
`run`, or a `Workflow` without `steps`. While it is possible to comment out `CommandLineTool` tool 
definitions in CWL YAML files (using `#`), these are then not usable by a `Workflow`. 

It is undesirable to leave a CWL file in an invalid state for long, in particular from graphical editors, 
as errors then accumulate and can be trickier to solve once the tool is desired.

For **use case 2** of multiple implementations, it is possible today to make multiple tools that have 
roughly the same input/output definitions, and change implementation by modifying `run` 
and potentially modifying the `in` source mapping. It is not possible to map the `out`, so the 
alternate implementation must have both matching output names and types, or be wrapped 
in an inner `Workflow`.

This is effectively [duck typing](https://en.wikipedia.org/wiki/Duck_typing), but can be
fragile as the workflow steps upstream and downstream may no longer be compatible with the 
type of the replaced implementation.  It is also difficult to do delayed choice of implementation
at runtime (e.g. as an override parameter to `cwl-runner`).

For **use case 3** it is possible to define extensions of CWL, but this requires each implementation 
to create additional [schema salad](https://www.commonwl.org/v1.1/SchemaSalad.html) class 
definitions and import these by hypermedia in the CWL.

For **use case 4** the current workaround is to parse the YAML of the CWL without the help of `cwltool`
validation or RDF conversion. This runs the risk of broken visualization 
(e.g. step 3 output fed as input to step 1).

For **use case 5** the current best practice is to separate each "phase" in a separate nested `Workflow`, 
which are then combined in a super-Workflow that becomes executable once all its parts are complete.


## Desired features

* Clear indication that a tool has not been implemented/chosen
* Typed inputs and outputs
* Versioned identifier of abstract tool
* Close in syntax to `CommandLineTool` and `Workflow`


## Proposed solution

There are two parts to this solution. 

### Abstract Operation

To solve use case 1, 3, 4, 5, add a new class `Operation`, which is similar to `CommandLineTool` and `Workflow`, but lacks `steps` and `run`:

```cwl
class: Operation
id: aligner
doc: Align the sequences
inputs:
  fasta:
    type: File
    format: edam:format_12345
outputs:
  bam:
    type: File
    format: edam:format_54321
```

It is recommended that as the abstract `Operation` is a _descriptive_ rather than _executable_ element of a workflow, the Operation SHOULD have `doc` to document its function, and each of the `inputs` and `outputs` MUST have `type` and SHOULD have `format` and `doc`.

### Multiple implementations

To address **use case 2** of multiple implementations the `id` of an `Operation` SHOULD be an absolute URI, which SHOULD include a [semantic version](https://semver.org/) number. Resolving the URI SHOULD return a CWL file that includes the same `Operation` definition.

```cwl
class: Operation
id: https://example.com/operations/align.cwl#v1.0.0
doc: Align the sequences
inputs:
  fasta:
    type: File
    format: edam:format_12345
outputs:
  bam:
    type: File
    format: edam:format_54321
```

Any tool (e.g. `CommandLineTool`, `ExpressionTool` or `Workflow`) can declare that they implements some operation(s) by using `implementsOperation` referring to the _Operation_ `id`:

```cwl
class: CommandLineTool
id: samtools
implementsOperation: 
 - https://example.com/operations/align.cwl#v1.0.0
 - https://example.com/operations/align.cwl#v1.1.0
doc: Align the sequences
inputs:
  fasta:
    type: File
    format: edam:format_12345
    inputBinding:
      # ...
outputs:
  bam:
    type: File
    format: edam:format_54321
run:  
```

### Type compatibility 

For each `implementsOperation` given, the `type` declared for the implementations inputs MUST be compatible with the `Operation`'s `inputs`, but MAY be more general (e.g. the _Operation_ can have `type: string` and the _CommandLineTool_ can have `type: string? | int`. Inversely, the implementation `outputs` MUST be compatible with the _Operation_'s type, but MAY be more specific.  Any additional `inputs` in the implementation MUST have a `default` or permit `null`.  Additional `outputs` from the implementation can be ignored.

### Inheritance

It is possible for an `Operation` to declare `implementsOperation` to another _Operation_ - this can be seen as a rudimentary subclassing of the abstract operation, where the same requirements applies as above. 

It is RECOMMENDED to declare backwards-compatible types (e.g. adding an optional input) in this way:

```cwl
class: Operation
id: https://example.com/operations/align.cwl#v1.1.0
implementsOperation: 
 - https://example.com/operations/align.cwl#v1.0.0
doc: Align the sequences
inputs:
  fasta:
    type: File
    format: edam:format_12345
  algorithm:
    type: string?
    doc: Optional algorithm to use
outputs:
  bam:
    type: File
    format: edam:format_54321
```

### Mapping considerations

The _short name_ of the implementations's port `id` must match the short name of the _Operation_. The short name is split from the last `#` or `/`. For instance, these identifiers are compatible:

* `fasta`
* `Tool4.cwl#fasta`
* `file:///tmp/Tool4.cwl#fasta`
* `http://example.com/packed.cwl#tool4/fasta`

It is advisable to introduce an intermedidate `Workflow` implementation to do non-trivial mapping, e.g. for port renaming.

### Selecting an implementation

It is engine-specific how an CWL implementation can select or prioritize between different implementing tools, for instance additional command line arguments to `cwl-runner` or a pre-configured tool. It is RECOMMENDED that implementations supporting `--pack` embed any such discovered implementations.

Conceptually one can consider an implementation as a slottable replacement for the `run` block, and thus manually editing the `run` field will continue to function as a workaround.
