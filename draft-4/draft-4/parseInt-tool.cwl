#!/usr/bin/env cwl-runner

class: ExpressionTool
requirements:
  - class: InlineJavascriptRequirement
cwlVersion: cwl:draft-4.dev1

inputs:
  file1:
    type: File
    inputBinding: { loadContents: true }

outputs:
  output:
    type: int

expression: "$({'output': parseInt(inputs.file1.contents)})"
