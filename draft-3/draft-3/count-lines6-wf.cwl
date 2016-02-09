#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-3

inputs:
    - { id: file1, type: {type: array, items: File} }
    - { id: file2, type: {type: array, items: File} }

outputs:
    - id: count_output
      type: {type: array, items: int}
      source: "#step1/output"

requirements:
  - class: ScatterFeatureRequirement
  - class: MultipleInputFeatureRequirement

steps:
  - id: step1
    run: wc3-tool.cwl
    scatter: "#step1/file1"
    inputs:
      - id: file1
        source: ["#file1", "#file2"]
        linkMerge: merge_nested
    outputs:
      - id: output
