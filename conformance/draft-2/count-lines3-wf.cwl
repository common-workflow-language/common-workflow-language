#!/usr/bin/env cwl-runner
"@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json"
class: Workflow
inputs:
    - id: "#file1"
      type:
        type: array
        items: File
outputs:
    - id: "#count_output"
      type:
        type: array
        items: int
      connect: {"source": "wc2-tool.cwl#output"}
steps:
  - id: "#step1"
    run: {id: wc2-tool.cwl}
    requirements:
      - class: Scatter
        scatter: "#step1file"
    inputs:
      - id: "#step1file"
        param: "wc2-tool.cwl#file1"
        connect: {"source": "#file1"}
    outputs:
      - param: "wc2-tool.cwl#output"
