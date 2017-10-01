#
# This is a two-step workflow which uses "revtool" and "sorttool" defined above.
#
class: Workflow
doc: "Reverse the lines in a document, then sort those lines."
cwlVersion: v1.0

# Requirements & hints specify prerequisites and extensions to the workflow.
# In this example, DockerRequirement specifies a default Docker container
# in which the command line tools will execute.
hints:
  - class: DockerRequirement
    dockerPull: debian:stretch-slim


# The inputs array defines the structure of the input object that describes
# the inputs to the workflow.
#
# The "reverse_sort" input parameter demonstrates the "default" field.  If the
# field "reverse_sort" is not provided in the input object, the default value will
# be used.
inputs:
  input:
    type: File
    doc: "The input file to be processed."
  reverse_sort:
    type: boolean
    default: true
    doc: "If true, reverse (decending) sort"

# The "outputs" array defines the structure of the output object that describes
# the outputs of the workflow.
#
# Each output field must be connected to the output of one of the workflow
# steps using the "connect" field.  Here, the parameter "#output" of the
# workflow comes from the "#sorted" output of the "sort" step.
outputs:
  output:
    type: File
    outputSource: sorted/output
    doc: "The output with the lines reversed and sorted."

# The "steps" array lists the executable steps that make up the workflow.
# The tool to execute each step is listed in the "run" field.
#
# In the first step, the "inputs" field of the step connects the upstream
# parameter "#input" of the workflow to the input parameter of the tool
# "revtool.cwl#input"
#
# In the second step, the "inputs" field of the step connects the output
# parameter "#reversed" from the first step to the input parameter of the
# tool "sorttool.cwl#input".
steps:
  rev:
    in:
      input: input
    out: [output]
    run: revtool.cwl

  sorted:
    in:
      input: rev/output
      reverse: reverse_sort
    out: [output]
    run: sorttool.cwl
