#!/usr/bin/env cwl-runner
class: Workflow
inputs:
    - id: "#file1"
      type: File
      default: {class: File, path: hello.txt}
outputs:
    - id: "#count_output"
      type: int
      source: "#step1.output"
steps:
  - id: "#step1"
    run: {import: wc2-tool.cwl}
    inputs:
      - id: "#step1.file1"
        source: "#file1"
    outputs:
      - id: "#step1.output"
