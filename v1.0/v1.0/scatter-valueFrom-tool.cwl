cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  scattered_message:
    type: string
    inputBinding:
      position: 2
  message:
    type: string
    inputBinding:
      position: 1
outputs:
  out_message:
    type: stdout
baseCommand: echo
