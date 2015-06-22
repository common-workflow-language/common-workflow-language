#!/usr/bin/env cwl-runner
class: Workflow

inputs:
    - { id: "#file1", type: File }

outputs:
    - id: "#count_output"
      type: int
      connect: {"source": "#step1_output"}

requirements:
  - class: SubworkflowFeatureRequirement

steps:
  - id: "#step1"
    run: {import: count-lines1-wf.cwl}
    inputs:
      - id: "#step1file1"
        param: "count-lines1-wf.cwl#file1"
        connect: {source: "#file1"}
    outputs:
      - { id: "#step1_output", param: "count-lines1-wf.cwl#count_output" }
