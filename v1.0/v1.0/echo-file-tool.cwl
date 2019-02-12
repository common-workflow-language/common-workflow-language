cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
baseCommand: [echo]
inputs:
  in:
    type: string
    inputBinding:
      position: 1
outputs:
  out:
    type: stdout

