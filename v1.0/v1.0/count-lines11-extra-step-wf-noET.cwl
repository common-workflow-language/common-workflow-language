#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs:
  file1: File?

outputs:
  wc_output:
    type: File
    outputSource: step1/output

steps:
  step0:
    run: cat-tool.cwl
    in:
      file1: file1
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

