#!/usr/bin/env cwl-runner
class: Workflow
inputs:
    - id: "#file1"
      type: { type: array, items: File }

outputs:
    - id: "#count_output"
      type: { type: array, items: int }
      connect: {"source": "#step1_output"}

requirements:
  - class: ScatterFeatureRequirement

steps:
  - id: "#step1"
    run: {import: wc2-tool.cwl}
    scatter: "#step1file"
    inputs:
      - id: "#step1file"
        param: "wc2-tool.cwl#file1"
        connect: {"source": "#file1"}
    outputs:
      - id: "#step1_output"
        param: "wc2-tool.cwl#output"
