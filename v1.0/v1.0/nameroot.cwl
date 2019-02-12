cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  file1: File
outputs:
  b: stdout
stdout: $(inputs.file1.nameroot).xtx
baseCommand: []
arguments: [echo, $(inputs.file1.basename), $(inputs.file1.nameroot), $(inputs.file1.nameext)]
