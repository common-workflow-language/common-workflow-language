#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs:
  file1: File?

outputs:
  count_output:
    type: int
    outputSource: step2/output

steps:
  step1:
    run: wc-tool.cwl
    in:
      file1:
        source: file1
        default:
          class: File
          location: whale.txt
    out: [output]

  step2:
    run: parseInt-tool.cwl
    in:
      file1: step1/output
    out: [output]
