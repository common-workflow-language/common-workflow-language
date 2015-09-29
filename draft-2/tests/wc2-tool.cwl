#!/usr/bin/env cwl-runner
class: CommandLineTool

requirements:
  - import: node-engine.cwl

inputs:
    - { id: "#file1", type: File, inputBinding: {} }
outputs:
    - id: "#output"
      type: int
      outputBinding:
        glob: output.txt
        loadContents: true
        outputEval:
            engine: node-engine.cwl
            script: "parseInt($self[0].contents)"
stdout: output.txt
baseCommand: wc
