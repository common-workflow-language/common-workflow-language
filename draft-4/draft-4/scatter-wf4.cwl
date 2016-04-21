#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
$graph:
- id: echo
  class: CommandLineTool
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
  arguments: ["-n", "foo"]
  stdout: step1_out

- id: main
  class: Workflow
  inputs:
    - id: inp1
      type: { type: array, items: string }
    - id: inp2
      type: { type: array, items: string }
  requirements:
    - class: ScatterFeatureRequirement
  steps:
    - id: step1
      scatter: ["#main/step1/echo_in1", "#main/step1/echo_in2"]
      scatterMethod: dotproduct
      inputs:
        - { id: echo_in1, source: "#main/inp1" }
        - { id: echo_in2, source: "#main/inp2" }
      outputs:
        - { id: echo_out}
      run: "#echo"

  outputs:
    - id: out
      source: "#main/step1/echo_out"
      type:
        type: array
        items: string
