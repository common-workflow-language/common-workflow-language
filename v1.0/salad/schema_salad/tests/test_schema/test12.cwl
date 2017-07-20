cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  - id: example_flag
    type: boolean
    inputBinding:
      position: 1
      prefix: -f
  - id: example_flag
    type: int
    inputBinding:
      position: 3
      prefix: --example-string

outputs: []
