#!/usr/bin/env cwl-runner
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
