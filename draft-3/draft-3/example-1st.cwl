class: CommandLineTool
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
baseCommand: echo
stdout: output.txt
