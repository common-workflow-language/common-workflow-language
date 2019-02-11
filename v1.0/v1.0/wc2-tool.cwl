#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
requirements:
  - class: InlineJavascriptRequirement
hints:
  ResourceRequirement:
    ramMin: 8

inputs:
    - { id: file1, type: File, inputBinding: {} }
outputs:
    - id: output
      type: int
      outputBinding:
        glob: output.txt
        loadContents: true
        outputEval: "$(parseInt(self[0].contents))"
stdout: output.txt
baseCommand: wc
