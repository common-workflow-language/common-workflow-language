#!/usr/bin/env cwl-runner
"@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json"
class: Workflow
inputs:
    - id: "#file1"
      type: File
    - id: "#file2"
      type: File
outputs:
    - id: "#count_output"
      type:
        type: array
        items: int
      connect: {"source": "#step1_output"}
steps:
  - id: "#step1"
    impl: wc2-tool.cwl
    inputs:
      - def: "wc2-tool.cwl#file1"
        connect:
          - "source": "#file1"
          - "source": "#file2"
    outputs:
      - def: "wc2-tool.cwl#output"
        id: "#step1_output"
