#!/usr/bin/env cwl-runner
"@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json"
class: Workflow
inputs:
    - id: "#file1"
      type: File
      default: {class: File, path: hello.txt}
outputs:
    - id: "#count_output"
      type: int
      connect: {"source": "#step1_output"}
steps:
  - id: "#step1"
    run: {import: wc2-tool.cwl}
    inputs:
      - param: "wc2-tool.cwl#file1"
        connect: {"source": "#file1"}
    outputs:
      - param: "wc2-tool.cwl#output"
        id: "#step1_output"
