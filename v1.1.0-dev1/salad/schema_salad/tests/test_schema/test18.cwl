class: CommandLineTool
cwlVersion: v1.0
baseCommand: echo
inputs:
  - id: input
    type: string?
    inputBinding: {}
outputs:
  - id: output
    type: string?
    outputBinding: {}
  - id: output1
    type: Filea
