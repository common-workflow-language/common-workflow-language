#!/usr/bin/env cwl-runner

cwlVersion: v1.0
$graph:

- id: echo
  class: CommandLineTool
  hints:
    ResourceRequirement:
      ramMin: 8
  inputs:
    first:
      type: string
      inputBinding:
        position: 1
    echo_in1:
      type: string
      inputBinding:
        position: 2
    echo_in2:
      type: string
      inputBinding:
        position: 3
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
    inp1:
      type:
        type: array
        items:
          type: record
          name: instr
          fields:
            - name: instr
              type: string
    inp2:
      type: { type: array, items: string }
  requirements:
    - class: ScatterFeatureRequirement
    - class: StepInputExpressionRequirement
  steps:
    step1:
      scatter: [echo_in1, echo_in2]
      scatterMethod: flat_crossproduct
      in:
        echo_in1:
          source: inp1
          valueFrom: $(self.instr)
        echo_in2: inp2
        first:
          source: inp1
          valueFrom: "$(self[0].instr)"
      out: [echo_out]
      run: "#echo"

  outputs:
    out:
      outputSource: step1/echo_out
      type:
        type: array
        items: string
