#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs: []

outputs:
  count_output:
    type: int
    outputSource: step2/output

steps:
  step0:
    run: null-expression3-tool.cwl
    in: []
    out: [ output ]

  step1:
    run: wc-tool.cwl
    in:
      file1:
        source: step0/output
        default:
          class: File
          location: whale.txt
    out: [output]

  step2:
    run: parseInt-tool.cwl
    in:
      file1: step1/output
    out: [output]
