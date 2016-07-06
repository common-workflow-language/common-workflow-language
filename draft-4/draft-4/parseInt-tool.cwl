#!/usr/bin/env cwl-runner

class: ExpressionTool
requirements:
  - class: InlineJavascriptRequirement
cwlVersion: cwl:v1.0.dev4

inputs:
  file1:
    type: File
    inputBinding: { loadContents: true }

outputs:
  output: int

expression: "$({'output': parseInt(inputs.file1.contents)})"
