#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}

inputs:
  i:
    type: int

outputs:
  o:
    type: int[]

expression: >
  ${return {'o': Array.apply(undefined, {length: inputs.i}).map(Number.call, Number)};}
