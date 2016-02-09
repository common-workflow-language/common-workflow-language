#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-3
requirements:
  - class: StepInputExpressionRequirement
  - class: InlineJavascriptRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  - id: a
    type: int
  - id: b
    type: int

outputs:
  - id: val
    type: string
    source: "#step1/echo_out"

steps:
  - id: step1
    run:
      id: echo
      class: CommandLineTool
      inputs:
        - id: c
          type: int
          inputBinding: {}
      outputs:
        - id: echo_out
          type: string
          outputBinding:
            glob: "step1_out"
            loadContents: true
            outputEval: $(self[0].contents)
      baseCommand: "echo"
      stdout: step1_out

    inputs:
      - {id: c, source: ["#a", "#b"], valueFrom: "$(self[0] + self[1])" }
    outputs:
      - {id: echo_out}
