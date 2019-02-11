#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  dir1:
    type: Directory
    inputBinding:
      valueFrom: $(self.listing[0].path)
outputs:
  output_file:
    type: File
    outputBinding: {glob: output.txt}
baseCommand: cat
stdout: output.txt
