#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs:
    file1: File

outputs:
    wc_output:
      type: File
      outputSource: step1/wc_output

requirements:
  - class: SubworkflowFeatureRequirement

steps:
  step1:
    run: count-lines1-wf-noET.cwl
    in:
      file1: file1
    out: [wc_output]
