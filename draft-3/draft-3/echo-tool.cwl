#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: cwl:draft-3
inputs:
  - id: in
    type: Any
    inputBinding: {}
outputs:
  - id: out
    type: string
    outputBinding:
      glob: out.txt
      loadContents: true
      outputEval: $(self[0].contents)
baseCommand: echo
stdout: out.txt
