#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow
inputs:
  inp:
    type:
      type: array
      items:
        type: record
        name: instr
        fields:
          - name: instr
            type: string
outputs:
  out:
    type:
      type: array
      items: string
    outputSource: step1/echo_out

requirements:
  - class: ScatterFeatureRequirement
  - class: StepInputExpressionRequirement

steps:
  step1:
    in:
      echo_in:
        source: inp
        valueFrom: $(self.instr)
      first:
        source: inp
        valueFrom: $(inputs.echo_in.instr)
    out: [echo_out]
    scatter: echo_in
    run:
      class: CommandLineTool
      hints:
        ResourceRequirement:
          ramMin: 8
      inputs:
        first:
          type: string
          inputBinding:
            position: 1
        echo_in:
          type: string
          inputBinding:
            position: 2
      outputs:
        echo_out:
          type: string
          outputBinding:
            glob: "step1_out"
            loadContents: true
            outputEval: $(self[0].contents)
      baseCommand: "echo"
      arguments:
        - "-n"
        - "foo"
      stdout: "step1_out"
