#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

inputs:
  i:
    type: int
    default: 4

outputs:
  o:
    type: int
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
          type: int
      outputs:
        o:
          type: int
      expression: >
        ${return {'o': (inputs.i || 2)};}
  step2:
    in:
      i: step1/o
    out: [o]
    run:
      class: ExpressionTool
      inputs:
        i:
          type: int
        i2:
          type: int
          default: 5
      outputs:
        o:
          type: int
      expression: >
        ${return {'o': inputs.i * 2 + inputs.i2};}
