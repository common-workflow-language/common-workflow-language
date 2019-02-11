#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8

inputs:
  file1: File

outputs:
  output:
    type: File
    outputBinding: { glob: output }

baseCommand: [wc, -l]

stdin: $(inputs.file1.path)
stdout: output
