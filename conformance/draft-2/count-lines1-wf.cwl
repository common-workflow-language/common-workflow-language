#!/usr/bin/env cwl-runner
"@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json"
class: Workflow
inputs:
  - id: "#file1"
    type: File
outputs:
  - id: "#count_output"
    type: int
    connect: {"source": "#step2_output"}
steps:
  - id: "#step1"
    impl: wc-tool.cwl
    inputs:
      - def: "wc-tool.cwl#file1"
        connect: {"source": "#file1"}
    outputs:
      - def: "wc-tool.cwl#output"
        id: "#step1_output"
  - id: "#step2"
    impl: parseInt-tool.cwl
    inputs:
      - def: "parseInt-tool.cwl#file1"
        connect: {"source": "#step1_output"}
    outputs:
      - def: "parseInt-tool.cwl#output"
        id: "#step2_output"
