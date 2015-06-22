#!/usr/bin/env cwl-runner

- id: "#echo"
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
      scatter: ["#step1.echo_in1", "#step1.echo_in2"]
      scatterMethod: dotproduct
      inputs:
        - { id: "#step1.echo_in1", source: "#inp1" }
        - { id: "#step1.echo_in2", source: "#inp2" }
      outputs:
        - { id: "#step1.echo_out"}
      run: {import: "#echo"}

  outputs:
    - id: "#out"
      source: "#step1.echo_out"
      type:
        type: array
        items: string
