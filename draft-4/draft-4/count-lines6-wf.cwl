#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-4.dev1

inputs:
    file1:
      type: {type: array, items: File}
    file2:
      type: {type: array, items: File}

outputs:
    count_output:
      type: {type: array, items: int}
      source: "#step1/output"

requirements:
  - class: ScatterFeatureRequirement
  - class: MultipleInputFeatureRequirement

steps:
  step1:
    run: wc3-tool.cwl
    scatter: "#step1/file1"
    in:
      file1:
        source: ["#file1", "#file2"]
        linkMerge: merge_nested
    out: [output]
