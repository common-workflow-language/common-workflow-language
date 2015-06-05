class: CommandLineTool
inputs:
  - id: "#input"
    type: File
    inputBinding: {}

outputs:
  - id: "#output"
    type: File
    outputBinding:
      glob: output.txt

baseCommand: rev
stdout: output.txt