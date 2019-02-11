#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

inputs:
  i: File

outputs:
  o:
    type: File[]
    outputSource: step2/o

steps:
  step1:
    in:
      i: i
    out: [o]
    run:
      class: ExpressionTool
      inputs:
        i:
          type: File
          inputBinding: { loadContents: true }

      outputs:
        o:
          type: string[]
      expression: >
        ${return {'o': inputs.i.contents.split(" ")};}
  step2:
    in:
      i:
        source: step1/o
    out: [o]
    run:
      class: CommandLineTool
      hints:
        ResourceRequirement:
          ramMin: 8

      inputs:
        i:
          type: string[]
          inputBinding:
            position: 1

      outputs:
        o:
          type: File[]
          outputBinding:
            glob: $(inputs.i)

      baseCommand: touch
