#!/usr/bin/env cwl-runner

class: ExpressionTool
requirements:
  - class: InlineJavascriptRequirement
cwlVersion: v1.1.0-dev1

inputs:
  file1:
    type: File
    inputBinding: { loadContents: true }

outputs:
  output: int

expression: "$({'output': parseInt(inputs.file1.contents)})"
