#!/usr/bin/env cwl-runner

- id: "#echo"
  class: CommandLineTool
  inputs:
    - id: "#echo_in1"
      type: string
      connect: {source: "#inp1"}
      inputBinding: {}
    - id: "#echo_in2"
      type: string
      connect: {source: "#inp2"}
      inputBinding: {}
  outputs:
    - id: "#echo_out"
      type: string
      outputBinding:
        glob: "step1_out"
        loadContents: true
        outputEval:
          class: Expression
          engine: cwl:JsonPointer
          script: "context/0/contents"
  baseCommand: "echo"
  arguments: ["-n", "foo"]
  stdout: step1_out

- id: "#main"
  class: Workflow
  inputs:
    - id: "#inp1"
      type: { type: array, items: string }
    - id: "#inp2"
      type: { type: array, items: string }
  requirements:
    - class: ScatterFeatureRequirement
  steps:
    - id: "#step1"
      scatter: ["#step1_in1", "#step1_in2"]
      scatterMethod: flat_crossproduct
      inputs:
        - { id: "#step1_in1", param: "#echo_in1", connect: {source: "#inp1"} }
        - { id: "#step1_in2", param: "#echo_in2", connect: {source: "#inp2"} }
      outputs:
        - { id: "#step1_out", param: "#echo_out" }
      run: {import: "#echo"}

  outputs:
    - id: "#out"
      connect: {source: "#step1_out"}
      type:
        type: array
        items:
          type: array
          items: string
