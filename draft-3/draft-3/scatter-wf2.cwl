#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
class: Workflow

inputs:
  - id: inp1
    type: { type: array, items: string }
  - id: inp2
    type: { type: array, items: string }

outputs:
  - id: out
    source: "#step1/echo_out"
    type:
      type: array
      items:
        type: array
        items: string

requirements:
  - class: ScatterFeatureRequirement

steps:
  - id: step1
    inputs:
      - { id: echo_in1, source: "#inp1"}
      - { id: echo_in2, source: "#inp2"}
    outputs:
      - id: echo_out

    scatter: ["#step1/echo_in1", "#step1/echo_in2"]
    scatterMethod: nested_crossproduct
    run:
      class: CommandLineTool
      id: step1command
      inputs:
        - id: echo_in1
          type: string
          inputBinding: {}
        - id: echo_in2
          type: string
          inputBinding: {}
      outputs:
        - id: echo_out
          type: string
          outputBinding:
            glob: "step1_out"
            loadContents: true
            outputEval: $(self[0].contents)
      baseCommand: "echo"
      arguments:
        - "-n"
        - "foo"
      stdout: step1_out
