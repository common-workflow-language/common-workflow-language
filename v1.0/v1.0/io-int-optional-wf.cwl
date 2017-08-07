#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

inputs:
  i:
    type: int?

outputs:
  o:
    type: int
    outputSource: step1/o

steps:
  step1:
    in:
      i: i
    out: [o]
    run:
      class: ExpressionTool
      inputs:
        i:
          type: int?
      outputs:
        o:
          type: int
      expression: >
        ${return {'o': (inputs.i || 2) * 2};}
