#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-4.dev1

inputs:
    file1:
      type: File

outputs:
    count_output:
      type: int
      source: "#step1/count_output"

requirements:
  - class: SubworkflowFeatureRequirement

steps:
  step1:
    run: count-lines1-wf.cwl
    in:
      file1: "#file1"
    out: [count_output]
