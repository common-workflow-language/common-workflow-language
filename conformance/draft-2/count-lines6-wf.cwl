#!/usr/bin/env cwl-runner
class: Workflow

inputs:
    - { id: "#file1", type: {type: array, items: File} }
    - { id: "#file2", type: {type: array, items: File} }

outputs:
    - id: "#count_output"
      type: {type: array, items: int}
      connect: {"source": "#step1_output"}

steps:
  - id: "#step1"
    run: {import: wc3-tool.cwl}
    requirements:
      - class: Scatter
        scatter: "#step1file1"
    inputs:
      - id: "#step1file1"
        param: "wc3-tool.cwl#file1"
        connect:
          - "source": "#file1"
          - "source": "#file2"
        linkMerge: merge_nested
    outputs:
      - { id: "#step1_output", param: "wc3-tool.cwl#output" }
