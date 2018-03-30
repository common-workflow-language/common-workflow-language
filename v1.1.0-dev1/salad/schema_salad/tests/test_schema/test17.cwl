class: CommandLineTool
cwlVersion: v1.0
baseCommand: cowsay
inputs:
  - id: input
    type: string?
    inputBinding:
      position: 0
outputs:
  - id: output
    type: string?
    outputBinding: {}
  - aa: moa
