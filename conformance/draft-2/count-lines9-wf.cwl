#!/usr/bin/env cwl-runner
class: Workflow

inputs: []

outputs:
  - id: "#count_output"
    type: int
    source: "#step2.output"

steps:
  - id: "#step1"
    run: {import: wc-tool.cwl}
    inputs:
      - id: "#step1.file1"
        default:
          class: File
          path: "whale.txt"
    outputs:
      - {id: "#step1.output"}

  - id: "#step2"
    run: {import: parseInt-tool.cwl}
    inputs:
      - {id: "#step2.file1", source: "#step1.output"}
    outputs:
      - {id: "#step2.output"}