#
# This is a two-step workflow which uses "revtool" and "sorttool" defined above.
#
class: Workflow
description: "Reverse the lines in a document, then sort those lines."
cwlVersion: cwl:draft-3

# Requirements & hints specify prerequisites and extensions to the workflow.
# In this example, DockerRequirement specifies a default Docker container
# in which the command line tools will execute.
hints:
  - class: DockerRequirement
    dockerPull: debian:8


# The inputs array defines the structure of the input object that describes
# the inputs to the workflow.
#
# The "reverse_sort" input parameter demonstrates the "default" field.  If the
# field "reverse_sort" is not provided in the input object, the default value will
# be used.
inputs:
  - id: input
    type: File
    description: "The input file to be processed."
  - id: reverse_sort
    type: boolean
    default: true
    description: "If true, reverse (decending) sort"

# The "outputs" array defines the structure of the output object that describes
# the outputs of the workflow.
#
# Each output field must be connected to the output of one of the workflow
# steps using the "connect" field.  Here, the parameter "#output" of the
# workflow comes from the "#sorted" output of the "sort" step.
outputs:
  - id: output
    type: File
    source: "#sorted/output"
    description: "The output with the lines reversed and sorted."

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
  - id: rev
    inputs:
      - { id: input, source: "#input" }
    outputs:
      - { id: output }
    run: revtool.cwl

  - id: sorted
    inputs:
      - { id: input, source: "#rev/output" }
      - { id: reverse, source: "#reverse_sort" }
    outputs:
      - { id: output }
    run: sorttool.cwl
