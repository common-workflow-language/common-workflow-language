#!/usr/bin/env cwl-runner
cwlVersion: v1.0
$graph:
- id: echo
  class: CommandLineTool
  hints:
    ResourceRequirement:
      ramMin: 8
  inputs:
    echo_in1:
      type: string
      inputBinding: {}
    echo_in2:
      type: string
      inputBinding: {}
  outputs:
    echo_out:
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
    inp1: string[]
    inp2: string[]
  requirements:
    - class: ScatterFeatureRequirement
  steps:
    step1:
      scatter: [echo_in1, echo_in2]
      scatterMethod: dotproduct
      in:
        echo_in1: inp1
        echo_in2: inp2
      out: [echo_out]
      run: "#echo"

  outputs:
    - id: out
      outputSource: step1/echo_out
      type:
        type: array
        items: string
