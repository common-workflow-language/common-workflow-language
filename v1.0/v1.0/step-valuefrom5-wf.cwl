#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0
requirements:
  - class: StepInputExpressionRequirement
  - class: InlineJavascriptRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  file1: File

outputs:
  val1:
    type: string
    outputSource: step1/echo_out
  val2:
    type: string
    outputSource: step2/echo_out

steps:
  step1:
    run:
      class: CommandLineTool

      inputs:
        name:
          type: string
          inputBinding: {}

      outputs:
        echo_out:
          type: string
          outputBinding:
            glob: "step1_out"
            loadContents: true
            outputEval: $(self[0].contents)
        echo_out_file:
          type: File
          outputBinding:
            glob: "step1_out"

      baseCommand: "echo"
      stdout: step1_out

    in:
      name:
        source: file1
        valueFrom: "$(self.basename)"
    out: [echo_out, echo_out_file]


  step2:
    run:
      class: CommandLineTool

      inputs:
        name:
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
      stdout: step1_out

    in:
      name:
        source: step1/echo_out_file
        valueFrom: "$(self.basename)"
    out: [echo_out]
