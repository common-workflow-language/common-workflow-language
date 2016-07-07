#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

requirements:
  - class: MultipleInputFeatureRequirement

inputs:
    file1:
      type: File[]
    file2:
      type: File[]

outputs:
    count_output:
      type: int
      outputSource: step1/output

steps:
  step1:
    run: wc3-tool.cwl
    in:
      file1:
        source: [file1, file2]
        linkMerge: merge_flattened
    out: [output]
