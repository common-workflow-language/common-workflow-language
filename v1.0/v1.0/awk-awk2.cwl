#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
inputs:
  atoBComparison:
    type: File
    inputBinding:
      position: 1
outputs:
  bRegionsNonZero:
    type: stdout
stdout: $(inputs.atoBComparison.basename)_nonZero.txt
baseCommand: awk
arguments: ["$5!=0"]
