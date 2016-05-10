#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-4.dev1

requirements:
  - class: MultipleInputFeatureRequirement

inputs:
    file1:
      type: {type: array, items: File}
    file2:
      type: {type: array, items: File}

outputs:
    count_output:
      type: int
      source: "#step1/output"

steps:
  step1:
    run: wc3-tool.cwl
    in:
      file1:
        source: ["#file1", "#file2"]
        linkMerge: merge_flattened
    out: [output]
