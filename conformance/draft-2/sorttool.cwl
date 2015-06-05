class: CommandLineTool
description: "Sort lines using the `sort` command"
inputs:
  - id: "#reverse"
    type: boolean
    inputBinding:
      position: 1
      prefix: "--reverse"
  - id: "#input"
    type: File
    inputBinding:
      position: 2

outputs:
  - id: "#output"
    type: File
    outputBinding:
      glob: output.txt

baseCommand: sort
stdout: output.txt