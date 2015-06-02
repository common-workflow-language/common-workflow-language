#!/usr/bin/env cwl-runner

class: CommandLineTool
inputs:
  - id: "#in"
    type: Any
    inputBinding: {}
outputs:
  - id: "#out"
    type: string
    outputBinding:
      glob: out.txt
      loadContents: true
      outputEval:
        engine: cwl:JsonPointer
        script: "/context/0/contents"
baseCommand: echo
stdout: out.txt