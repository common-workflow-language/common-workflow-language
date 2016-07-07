#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs:
    file1: File

outputs:
    count_output:
      type: int
      outputSource: step1/count_output

requirements:
  - class: SubworkflowFeatureRequirement

steps:
  step1:
    run: count-lines1-wf.cwl
    in:
      file1: file1
    out: [count_output]
