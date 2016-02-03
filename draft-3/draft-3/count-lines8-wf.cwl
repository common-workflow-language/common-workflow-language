#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-3

inputs:
    - { id: file1, type: File }

outputs:
    - id: count_output
      type: int
      source: "#step1/count_output"

requirements:
  - class: SubworkflowFeatureRequirement

steps:
  - id: step1
    run: count-lines1-wf.cwl
    inputs:
      - id: file1
        source: "#file1"
    outputs:
      - { id: count_output }
