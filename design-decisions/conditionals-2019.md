# Conditionals (2019)

## Abstract

This is a documentation of the decisions made in the design of conditionals outlined in 
[issue 854](https://github.com/common-workflow-language/common-workflow-language/issues/854)
For the specification of the feature please see that issue and the CWL specifications document.

## Conditionals in the context of CWL

The CWL 1.0 specification envisages a CWL workflow as a DAG of nodes each of
which is always executed. The scheduler/runner only decides when to run each
node.

Conditional execution in CWL adds features to a CWL document that enables the 
runner to skip execution of one or more nodes based on evaluation of one or
more parameter or expression evaluations.


## Need for conditionals in CWL

The initiative to implement conditionals in CWL has a long history. 
There is a long and illuminating thread on the [CWL mailing list](https://groups.google.com/d/topic/common-workflow-language/JU7PSEKr97M/discussion)
on this topic. There have been several proposals on the [github issues section](https://github.com/common-workflow-language/common-workflow-language/issues?q=is%3Aissue+is%3Aopen+label%3Aconditionals)

In short, while there is a minority sentiment that CWL should remain a pure dataflow 
language with no conditionals, there is a majority sentiment that, in the face of
reality, users need the ability to instruct the CWL runner on conditional execution.


## Alternatives to explicit conditionals for CWL

Workflows with conditional executions have been implemented in CWL 1.0. 
The basic pattern is to use javascript expressions to alter the command line of individual
tools. Based on the javascript expression a tool can be made to produce a dummy result,
or a different result.

While this can give the correct computational result it is extremely cumbersome and
non-transparent to the developer/user/auditor and it is non-optimal in terms of resource
usage - the scheduler still needs to prepare resources for a task, stage files etc. which
is wasteful.

It is also impractical to implement this on the workflow level, forcing the intrepid
developer to mangle all tools in a conditional branch. 


## Desirable properties for conditionals in CWL

After portability, one of the major benefits of describing workflows in CWL
is that the intent of the workflow is apparent from the structure. A workflow 
can, for example, be visualized as a data flow diagram for easy review and
auditing. It would be important to maintain this explicitness for conditionals. 

Next, it is important to minimize the complexity of the syntax, reducing the 
amount of CWL code needed to add conditionals to a workflow and the number of new
concepts introduced.

While the difficulty for workflow executor developers should be considered,
it is more important to make life easier for workflow developers.


### Example code

```
class: Workflow
cwlVersion: v1.conditionals-dev
inputs:
  in1: string
  val: int

steps:

  step1:
    in:
      in1: val
      a_new_var: val
    run: ../tools/foo.cwl
    runIf: $(inputs.a_new_var > 1)
    out: [out1]  # out1 is of type string

outputs:
  out1: 
    type: string
    outputSource:
      - step1/out1
      - in1
    branchSelect: first_that_ran 

requirements: 
  InlineJavascriptRequirement: {}
```

The new syntax adds a single field to `WorkflowStep` (`runIf`) and a new 
operator called `branchSelect` to the `WorkflowStepInput` and 
`WorkflowOutputParameter`. This is a fairly non-intrusive 
modification, fully backwards compatible (it's an addition, not a modification) and allows
developers to easily modify existing workflows with an intuitive syntax.

The most common pattern - a by-pass, e.g. as used when deciding whether to run a BAM indexer
or just pass on a BAM file - is very easy to implement.

### runIf

The `runIf` field allows the workflow developer to isolate the trigger condition
for whether a conditional step should run or not into a single explicit field.
This makes it easy for a reader to determine if a step can be conditional and
makes it easy for Visual Programming editors and other tools to mark the step
as conditional and show at least the conditional expression so an auditor can
inspect what triggers the step.

### branchSelect

The major complexity introduced by conditionals (in any language
framework) is that now a variable that was going to be consumed by a downstream
entity can be undefined. For example you can write the following in Python

```
if my_condition:
    foo = 24

bar(foo)
```
A good code editor will now warn you that `foo may be undefined` because there
is a code path where that happens, leading to bad things.

In a CWL workflow where type safety is a high priority the first guard against
the equivalent of an undefined variable is that all outputs of a skipped step
that are otherwise not handled are converted to the CWL `null` type. 

Therefore, static checkers should raise a type error if the sole source for a
required input is the output from a conditional step.

A workflow developer will, in most cases, want to treat a skipped step not
as a step that produced a `null` but rather as a step that never existed in
the first place. `branchSelect` serves this purpose, helping the workflow
developer filter skipped inputs to a downstream sink while maintaining type
consistency.

For detailed use cases for each kind of `branchSelect` see the specification.


### Why not introduce a new process object?

A proposal for a new process object ([`Switch`](https://github.com/common-workflow-language/common-workflow-language/issues/789)) was considered. Preliminary experimentation
with the syntax raised the complaint that it was quite verbose and unwieldy
for the most common use cases, which were to by-pass a step. As can be seen
from the example above, which implements this common by-pass pattern, the
`runIf` syntax is quite succinct and explicit for this use case.

There are two attractions to using a process object from a language safety
point of view
1. Isolation of conditional variables to a separate process object
2. Ability to implement `if-else` and `switch-default` patterns

The first point is addressed by `branchSelect` and the fallback of filling
undefined values with `null` if no `branchSelect` is supplied.

The second point is an important factor in favor of a new process object and
is further discussed below

### No safe/cheap `if-else`, `switch-default` construct

In the current design the developer has to write an explicit expression that
serves as an `else` or  `default` condition. While 
`branchSelect: the_one_that_ran` allows a user to verify they get the correct 
behavior during execution, a developer has to be careful about the expressions 
in these fall back conditions. 

The `if-else` or `switch-case` construct can be implemented by using `runIf`
in combination with `branchSelect: the_first_that_ran`. The drawback is that
the `else` or `default` step will always run even if it's output is not used.

On the one hand, this demands extra vigilance and work on the part of the 
workflow developer. On the other hand there may be applications where 
having to explicitly think about the condition for each case without having
recourse to an automatic fallback can remove sources of bugs.

In programing languages `if-else` constructs utilize the concept of a code block
and the two halves of the `if-else` or the clauses of a `switch` form a collection
of function invocations or commands that are grouped together.

In order to introduce this kind of behavior in CWL where workflow steps that don't
run can influence whether another step runs or not, we would need to 
either add a specialized process step (as proposed in the [switch process][switch])
or to add notations in the steps linking them together as a block.

[switch]: https://github.com/common-workflow-language/common-workflow-language/issues/789

The Switch proposal offers greater auditability and makes things easier to
reason about but is much more verbose.

As a compromise we introduce this minimally disruptive syntax, with the given
limitations with the intention that if user feedback indicates the `default`
cases are important we should add a Switch like construct which will allow
such safer constructs with the cost of more code.


## Future expansion

### Smart inference of `branchSelect`
In most cases the `branchSelect` value can be infered based on the 
type of the sink port and the nature of the source steps. Because of this
we can write some explicit rules for `branchSelect` inference

Use `the_first_that_ran` when
1. sink is of type `T` and all sources are of type `T` AND
1. There is exactly one source which does not come from a conditional step

Use `the_one_that_ran` when
1. sink is of type `T` and all sources are of type `T` AND
1. Every source comes from a conditonal step

Use `all_that_ran` when
1. sink is of type `[T]` and all sources are of type `T`


### More detailed validation warnings
We can warn the user they may have an unintended pattern if
1. User has `branchSelect: the_first_that_ran` and has sources
   from un-conditional steps in the middle of the list
1. User has `branchSelect: the_one_that_ran` and has one or
   more sources from un-conditional steps



### Provision for `if-else` and `switch-default` constructs
As discussed before this adds cognitive burden for the user 
and additional state tracking for the runner developer. 
This feature may be added if there is substantial user feedback
that the additional complexity on all fronts is important. The
most user friendly path will probbaly be to resurrect the `Switch` statement proposal.

