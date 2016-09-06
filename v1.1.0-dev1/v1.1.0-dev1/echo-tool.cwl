#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.1.0-dev1
inputs:
  in:
    type: Any
    inputBinding: {}
outputs:
  out:
    type: string
    outputBinding:
      glob: out.txt
      loadContents: true
      outputEval: $(self[0].contents)
baseCommand: echo
stdout: out.txt
