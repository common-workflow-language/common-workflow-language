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





