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


## Walkthrough of proposed syntax with commentary on design decisions 


### Example code

```
class: Workflow
cwlVersion: v1.2.0-dev1
inputs:
  val: int

steps:

  step0:
    in:
      in1: val
      a_new_var: val
    run: ../tools/foo.cwl
    when: $(inputs.a_new_var > 1)
    out: [out1]


  step1:
    in:
      in1: val
      a_new_var: val
    run: ../tools/bar.cwl
    when: $(inputs.a_new_var < 1)
    out: [out1]

outputs:
  out1: 
    type: string
    outputSource:
        - step0/out1
        - step1/out1
    pickValue: first_non_null

requirements: 
  InlineJavascriptRequirement: {}
```

The new syntax adds a single field to `WorkflowStep` (`when`) and a new 
operator called `pickValue` to the `WorkflowStepInput` and 
`WorkflowOutputParameter`. This is a fairly non-intrusive 
modification, fully backwards compatible (it's an addition, not a modification) and allows
developers to easily modify existing workflows with an intuitive syntax.
Additionally, the `pickValue` field describes an operator that
can exist independent of conditional steps.

### when

```
  step0:
    in:
      in1: val
      a_new_var: val
    run: ../tools/foo.cwl
    when: $(inputs.a_new_var > 1)
    out: [out1]
```

The `when` field allows the workflow developer to isolate the trigger condition
for whether a conditional step should run or not into a single explicit field.
This makes it easy for a reader to determine if a step can be conditional and
makes it easy for Visual Programming editors and other tools to mark the step
as conditional and show at least the conditional expression so an auditor can
inspect what triggers the step.

### Skipped steps produce `null` on every output

In an initial design, skipped steps produced a special internal object called
a `skipNull`. The `skipNull` was introduced in order to inform downstream 
sinks that this value comes from a skipped step.

When outputs from conditional steps converged on a sink, 
a proposed operator called `branchSelect` was introduced, which
handled these `skipNull` objects according to the desired pattern. After
passing through `branchSelect` all the `skipNull` objects were removed
leaving behind inputs that behaved as if the skipped steps never ran.
If `branchSelect` was not used the `skipNull`s were converted to nulls
with a warning.

After a discussion initiated by @jmchilton it was decided to further
simplify the concepts have skipped steps just produce `null`. Now we
can now no longer distinguish between a `null` produced by a step that
ran and a `null` produced by a skipped step. It was decided that if
an important use case arose where it was absoluetly vital to be able
to distinguish the sources of `null`, we would make additions to the
specification to handle it.


### pickValue

The first disruptive concept introduced by conditionals is that a step
can now NOT run. The scope of this disruption has been confined by
mandating that a skipped step produce `null` values on its outputs,
bringing the produced type into the universe of allowed CWL types.

Perhaps even more disruptive than this first concept is the consideration
that now a scalar sink can now recieve multiple inputs. 

```
outputs:
  out1: 
    type: string
    outputSource:
        - step0/out1
        - step1/out1
    pickValue: first_non_null
```

Our intention here is that only one of these two inputs (the one
that ran) should be fed into `out1`. In order to confine and make this
disruption tractable we have introduced the `pickValue` operator.
This sits at the same level as the existing `linkMerge` operator and
also operates on lists of inputs. Just like the `linkMerge` 
operator can convert a list of lists into a single list, the `pickValue`
operator can convert a list into a scalar by filtering out any `null`
values in the list. Combining `when` and `pickValue` allows us to 
describe the common conditional processing patterns, as listed in
the [proposal](https://github.com/common-workflow-language/common-workflow-language/issues/854)


### pickValue does not recurse into a list
It was decided during a discussion ( [2019.10.05](https://docs.google.com/document/d/1Fd3KR2Nhl22yh_09V2PoFrTGsZGEkhs2qj_19Q4I9VQ/edit)) that
the `pickValue` operator would only filter out nulls at the top level of the list.
This serves the purpose of allowing `pickValue` to handle cases (as described above)
where multiple inputs feed into a scalar port, while not creating any surprising
changes within a list of lists, when, for example, two lists are combined in
parallel. An example is given [here](https://github.com/kaushik-work/cwl-conditionals/blob/master/workflows/scatter-3.cwl)
This principle of least surprise was first proposed by @pvanheus.

In case a valid use case is later presented, an addition to the specification may
be made, that can be used to require `pickValue` or some similar operator to
recurse into nested lists.

### pickValue is at the same level as linkMerge

@jmchilton proposed at the Boston, October 2019, CWL mini-conference that the `pickValue` operator be placed beneath 
the source operator. Looking like

```
outputs:
  out1: 
    type: string
    outputSource:
      first_non_null:
        - step0/out1
        - step1/out1
```
This syntax has a great virtue of being very obvious to read. It makes it very clear what is happening
with the two inputs and how they are being fed into `out1`. @kaushik-work proposed, however, that
it creates an in-congruence with the existing `linkMerge` operator. Also, during the meeting of
2019.10.05, it was formally decided that
a) the `linkMerge` operator would operate first and
b) `pickValue` would not recurse into the lists

This makes this proposed syntax mis-leading, since it suggests that `first_non_null` operates before
`linkMerge`.

For these reason it was decided to have the `pickValue` operator sit at the same level as `linkMerge`
to emphasize the kinship between these two operators.


### Commentary on `null`

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
produce a CWL `null` type. Static checkers should, therefore, raise a type 
error if the sole source for a required input is the output from a conditional step.

A workflow developer will, in most cases, want to treat a skipped step not
as a step that produced a `null` but rather as a step that never existed in
the first place. `pickValue` serves this purpose, helping the workflow
developer filter skipped inputs to a downstream sink while maintaining type
consistency.

For detailed use cases for each kind of `pickValue` see the specification.


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

