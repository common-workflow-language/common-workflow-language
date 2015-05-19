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
      connect: {"source": "#step1_output"}
requirements:
  - class: ScatterFeature
steps:
  - id: "#step1"
    class: External
    impl: wc2-tool.cwl
    inputs:
      - id: "#step1file"
        def: "wc2-tool.cwl#file1"
        connect: {"source": "#file1"}
    outputs:
      - def: "wc2-tool.cwl#output"
        id: "#step1_output"
    scatter: "#step1file"
