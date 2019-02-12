class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8
baseCommand: [tar, xvf]
inputs:
  inf:
    type: File
    inputBinding:
      position: 1
outputs:
  outdir:
    type: Directory
    outputBinding:
      glob: .
