#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

inputs:
  bar:
    type:
    - File
    - 'null'
    - string
    default: the default value

outputs:
  o:
    type: string
    outputSource: step1/o

steps:
  step1:
    in:
      i: bar
    out: [o]
    run:
      class: ExpressionTool
      inputs:
        i:
          type:
          - File
          - 'null'
          - string
      outputs:
        o:
          type: string
      expression: >
        ${return {'o': (inputs.i.class || inputs.i)};}
