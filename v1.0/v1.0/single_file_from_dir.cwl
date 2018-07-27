#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow

requirements:
  StepInputExpressionRequirement: {}

inputs:
  inf: File  # tarfile
outputs:
  output:
    type: File
    outputSource: second/output

steps:
  first:
    run: dir3.cwl
    in:
      inf: inf
    out: [ outdir ]
  second:
    run: cat-tool.cwl
    in:
      file1:
        source: first/outdir
        valueFrom: $(self.listing[0])
    out: [ output ]
      
