#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-3

inputs:
    - id: file1
      type: File
      default: {class: File, path: hello.txt}
outputs:
    - id: count_output
      type: int
      source: "#step1/output"
steps:
  - id: step1
    run: wc2-tool.cwl
    inputs:
      - id: file1
        source: "#file1"
    outputs:
      - id: output
