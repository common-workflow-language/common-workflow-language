#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-4.dev1
requirements:
  - class: StepInputExpressionRequirement
  - class: InlineJavascriptRequirement

inputs:
  a: int
  b: int

outputs:
  val:
    type: string
    source: "#step1/echo_out"

steps:
  step1:
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

    in:
      a: "#a"
      b: "#b"
      c:
        valueFrom: "$(inputs.a + inputs.b)"
    out: [echo_out]
