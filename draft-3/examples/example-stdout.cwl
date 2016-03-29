cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: echo
stdout: output.txt
inputs:
  - id: message
    type: string
    inputBinding:
      position: 1
outputs:
  - id: output
    type: File
    outputBinding:
      glob: output.txt
