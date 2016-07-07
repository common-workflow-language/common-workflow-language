#!/usr/bin/env cwl-runner

class: ExpressionTool
requirements:
  - class: InlineJavascriptRequirement
cwlVersion: v1.0

inputs:
  i1: Any

outputs:
  output: int

expression: "$({'output': (inputs.i1 == 'the-default' ? 1 : 2)})"