class: CommandLineTool
inputs:
  - id: pattern
    type: string
    inputBinding:
      position: 1
  - id: input
    type: File
    inputBinding:
      position: 2
outputs:
  - id: output
    type: File
    outputBinding:
      glob: grep.txt
baseCommand: grep
stdout: grep.txt
