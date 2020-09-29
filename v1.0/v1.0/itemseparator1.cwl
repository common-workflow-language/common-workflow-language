#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: "v1.0"
doc: "Test itemSeparator with prefix"
hints:
  ResourceRequirement:
    ramMin: 8
    coresMax: 1
inputs:
  i:
    type: string[]
    label: Input File
    doc: "Echo these strings"
    inputBinding: 
      position: 1
      prefix: a
      itemSeparator: " c "
outputs:
  o:
    type: File
    outputBinding:
      glob: output.txt
baseCommand: echo
stdout: output.txt
