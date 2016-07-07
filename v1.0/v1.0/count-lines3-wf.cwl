#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs:
    file1:
      type: File[]

outputs:
    count_output:
      type: int[]
      outputSource: step1/output

requirements:
  ScatterFeatureRequirement: {}

steps:
  step1:
    run: wc2-tool.cwl
    scatter: file1
    in:
      file1: file1
    out: [output]
