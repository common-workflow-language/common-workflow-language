#!/usr/bin/env cwl-runner

class: ExpressionTool
requirements:
  - class: InlineJavascriptRequirement
cwlVersion: v1.1.0-dev1

inputs:
  i1:
    type: Any
    default: "the-default"

outputs:
  output: int

expression: "$({'output': (inputs.i1 == 'the-default' ? 1 : 2)})"