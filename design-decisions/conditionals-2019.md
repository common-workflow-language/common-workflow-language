# Conditionals (2019)

## Abstract

This is a documentation of the decisions made in the design of conditionals outlined in 
[issue 854](https://github.com/common-workflow-language/common-workflow-language/issues/854)
For the specification of the feature please see that issue and the CWL specifications document.


## Need for conditionals in CWL

The initiative to implement conditionals in CWL has a long history. 
There is a long and illuminating thread on the [CWL mailing list](https://groups.google.com/d/topic/common-workflow-language/JU7PSEKr97M/discussion)
on this topic. There have been several proposals on the [github issues section](https://github.com/common-workflow-language/common-workflow-language/issues?q=is%3Aissue+is%3Aopen+label%3Aconditionals)

In short, while there is a minority sentiment that CWL should remain a pure dataflow 
language with no conditionals, there is a majority sentiment that, in the face of
reality, users need the ability to instruct the CWL runner on conditional execution.


## Alternatives to explicit conditionals for CWL

Workflows that have conditional executions can and have been implemented in CWL 1.0. 
The basic pattern is to use javascript expressions to alter the command line of individual
tools. Based on the javascript expression a tool can be made to produce a dummy result,
or a different result.

While this can give the correct computational result it is extremely cumbersome and
non-transparent to the developer/user/auditor and it is non-optimal in terms of resource
usage - the scheduler still needs to prepare resources for a task, stage files etc. which
is wasteful.

It is also impractical to implement this on the workflow level, forcing the intrepid
developer to mangle all tools in a conditional branch. 

## Major decision points (optimizations)

- Minimize disruption to current syntax
- Minimize the number of new concepts exposed to the user
- Minimize amount of text developer has to write
- Make auditable (make it easily apparent what is a conditional and in what way)
- Minimize the number of new concepts exposed to the runner developer

The new syntax adds a single field to `WorkflowStep` and a new operator called `branchSelect` 
to the `WorkflowStepInput` and `WorkflowOutputParameter`. This is a fairly non-intrusive 
modification, fully backwards compatibile (it's an addition, not a modification) and allows
developers to easily modify existing workflows with an intuitive syntax.

The most common pattern - a by-pass, e.g. as used when deciding whether to run a BAM indexer
or just pass on a BAM file - is very easy to implement.


### No explicit `if-else` construct
Some thought went into the the `if-else` pattern as well as the `switch-default` pattern.
In the current design the developer has to actively choose an `else` or 
`default` conditon. This can be easy to mess-up, especially for long `switch` like constructs.

If the developer wishes not to explicitly invert the conditions
they have to use the `by-pass` pattern (`branchSelect: the_first_that_ran`) and implement
the `else` or `default` step as un-conditional. This is wasteful since the step will
always run.

The problem with this construct is that it requires the concept of a block and a concept of
the runner being able to run a step based on whether other, potentially unconnected, steps 
have been skipped.

In CWL the isolated code block is a workflow. The only existing way to make one step depend
upon another is to connect them (creating an input dependency).

A `if-else` or `switch-default` construct would become unmanageable without isolating all the
cases into a separate workflow (see https://github.com/common-workflow-language/common-workflow-language/issues/789)
which has a special property that the steps are run in a particular order and a special
step (called `default`) is available and will only run if none of the other steps run.

The user feedback for this construct was that it was fairly cumbersome, requiring the overhead of
writing out a separate nested process object (a `Switch`) each time a conditional was required.

In a future iteration of conditionals we should consider creating a new process object called
`Switch` that has the explicit goal of addressing this use case at the expense of more verbose
syntax.


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

