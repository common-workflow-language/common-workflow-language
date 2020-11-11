#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

inputs:
  in:
    type: File
    inputBinding: {position: 1}
outputs:
  contains_b:
    type: boolean
    outputBinding:
      glob: out.txt
      loadContents: true
      outputEval: $(self[0].contents.indexOf("b") >= 0)
baseCommand: cat
stdout: out.txt
