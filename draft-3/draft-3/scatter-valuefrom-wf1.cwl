#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
class: Workflow
inputs:
  - id: inp
    type:
      type: array
      items:
        type: record
        name: instr
        fields:
          - name: instr
            type: string
outputs:
  - id: out
    type:
      type: array
      items: string
    source: "#step1/echo_out"

requirements:
  - class: ScatterFeatureRequirement
  - class: StepInputExpressionRequirement

steps:
  - id: step1
    inputs:
      - {id: echo_in, source: "#inp", valueFrom: $(self.instr) }
      - {id: first, source: "#inp", valueFrom: "$(self[0].instr)" }
    outputs:
      - id: echo_out
    scatter: "#step1/echo_in"
    run:
      class: CommandLineTool
      inputs:
        - id: first
          type: string
          inputBinding:
            position: 1
        - id: echo_in
          type: string
          inputBinding:
            position: 2
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
      stdout: "step1_out"
