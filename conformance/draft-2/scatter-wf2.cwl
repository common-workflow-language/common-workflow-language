#!/usr/bin/env cwl-runner

class: Workflow

inputs:
  - id: "#inp1"
    type: { type: array, items: string }
  - id: "#inp2"
    type: { type: array, items: string }

steps:
  - id: "#step1"
    inputs:
      - { id: "#step1_in1", param: "#echo_in1", connect: {source: "#inp1"} }
      - { id: "#step1_in2", param: "#echo_in2", connect: {source: "#inp2"} }
    outputs:
      - { id: "#step1_out", param: "#echo_out" }
    requirements:
      - class: Scatter
        scatter: ["#step1_in1", "#step1_in2"]
        scatterMethod: nested_crossproduct
    run:
      class: CommandLineTool
      inputs:
        - id: "#echo_in1"
          type: string
          inputBinding: {}
        - id: "#echo_in2"
          type: string
          inputBinding: {}
      outputs:
        - id: "#echo_out"
          type: string
          outputBinding:
            glob: "step1_out"
            loadContents: true
            outputEval:
              engine: cwl:JsonPointer
              script: "context/0/contents"
      baseCommand: "echo"
      arguments:
        - "-n"
        - "foo"
      stdout: step1_out

outputs:
  - id: "#out"
    connect: {source: "#step1_out"}
    type:
      type: array
      items:
        type: array
        items: string
