cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: echo
inputs:
  - id: example_flag
    type: boolean
    inputBinding:
      position: 1
      prefix: -f
  - id: example_string
    type: string
    inputBinding:
      position: 3
      prefix: --example-string
  - id: example_int
    type: int
    inputBinding:
      position: 2
      prefix: -i
      separate: false
  - id: example_file
    type: ["null", File]
    inputBinding:
      prefix: --file=
      separate: false
      position: 4

outputs: []
