#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs: []

outputs:
  wc_output:
    type: File
    outputSource: step1/output

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
