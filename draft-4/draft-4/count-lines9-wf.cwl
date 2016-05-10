#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-4.dev1

inputs: []

outputs:
  count_output:
    type: int
    source: "#step2/output"

steps:
  step1:
    run: wc-tool.cwl
    in:
      file1:
        default:
          class: File
          path: whale.txt
    out: [output]

  step2:
    run: parseInt-tool.cwl
    in:
      file1: "#step1/output"
    out: [output]
