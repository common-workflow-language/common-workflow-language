#!/usr/bin/env cwl-runner
"@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json"
class: CommandLineTool
requirements:
  - id: node-engine.cwl
inputs:
    - id: "#file1"
      type: File
      inputBinding: {}
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
