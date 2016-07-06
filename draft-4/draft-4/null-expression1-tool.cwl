#!/usr/bin/env cwl-runner

class: ExpressionTool
requirements:
  - class: InlineJavascriptRequirement
cwlVersion: cwl:v1.0.dev4

inputs:
  i1:
    type: Any
    default: "the-default"

outputs:
  output: int

expression: "$({'output': (inputs.i1 == 'the-default' ? 1 : 2)})"