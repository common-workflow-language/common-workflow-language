class: CommandLineTool
cwlVersion: v1.0.dev4
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
