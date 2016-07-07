cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: touch
inputs:
  - id: touchfiles
    type:
      type: array
      items: string
    inputBinding:
      position: 1
outputs:
  - id: output
    type:
      type: array
      items: File
    outputBinding:
      glob: "*.txt"
