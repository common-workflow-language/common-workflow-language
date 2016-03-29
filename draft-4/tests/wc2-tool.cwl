#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: cwl:draft-4.dev1
requirements:
  - class: InlineJavascriptRequirement

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
