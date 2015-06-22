#!/usr/bin/env cwl-runner
class: Workflow

inputs:
    - { id: "#file1", type: {type: array, items: File} }
    - { id: "#file2", type: {type: array, items: File} }

outputs:
    - id: "#count_output"
      type: {type: array, items: int}
      source: "#step1.output"

requirements:
  - class: ScatterFeatureRequirement

steps:
  - id: "#step1"
    run: {import: wc3-tool.cwl}
    scatter: "#step1.file1"
    inputs:
      - id: "#step1.file1"
        source: ["#file1", "#file2"]
        linkMerge: merge_nested
    outputs:
      - id: "#step1.output"
