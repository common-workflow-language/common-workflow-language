#!/usr/bin/env cwl-runner
class: Workflow

inputs:
    - { id: "#file1", type: {type: array, items: File} }
    - { id: "#file2", type: {type: array, items: File} }

outputs:
    - id: "#count_output"
      type: int
      source: "#step1.output"

steps:
  - id: "#step1"
    run: {import: wc3-tool.cwl}
    inputs:
      - id: "#step1.file1"
        source: ["#file1", "#file2"]
        linkMerge: merge_flattened
    outputs:
      - { id: "#step1.output" }
