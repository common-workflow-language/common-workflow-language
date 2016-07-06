cwlVersion: cwl:draft-3
class: CommandLineTool
inputs:
  - id: filesA
    type:
      type: array
      items: string
    inputBinding:
      prefix: -A
      position: 1

  - id: filesB
    type:
      type: array
      items: string
      inputBinding:
        prefix: -B=
        separate: false
    inputBinding:
      position: 2

  - id: filesC
    type:
      type: array
      items: string
    inputBinding:
      prefix: -C=
      itemSeparator: ","
      separate: false
      position: 4

outputs: []
baseCommand: echo
