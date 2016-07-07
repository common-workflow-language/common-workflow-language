#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0
requirements:
  - class: StepInputExpressionRequirement
  - class: InlineJavascriptRequirement

inputs:
  a: int
  b: int

outputs:
  val:
    type: string
    outputSource: step1/echo_out

steps:
  step1:
    run:
      id: echo
      class: CommandLineTool
      inputs:
        c:
          type: int
          inputBinding: {}
      outputs:
        echo_out:
          type: string
          outputBinding:
            glob: "step1_out"
            loadContents: true
            outputEval: $(self[0].contents)
      baseCommand: "echo"
      stdout: step1_out

    in:
      a: a
      b: b
      c:
        valueFrom: "$(inputs.a + inputs.b)"
    out: [echo_out]
