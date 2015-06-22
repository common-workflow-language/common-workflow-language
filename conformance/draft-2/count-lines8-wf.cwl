#!/usr/bin/env cwl-runner
class: Workflow

inputs:
    - { id: "#file1", type: File }

outputs:
    - id: "#count_output"
      type: int
      source: "#step1.count_output"

requirements:
  - class: SubworkflowFeatureRequirement

steps:
  - id: "#step1"
    run: {import: count-lines1-wf.cwl}
    inputs:
      - id: "#step1.file1"
        source: "#file1"
    outputs:
      - { id: "#step1.count_output" }
