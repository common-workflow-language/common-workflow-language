class: CommandLineTool
cwlVersion: v1.0
requirements:
- class: InlineJavascriptRequirement
inputs:
  - id: array_input
    type:
      - type: array
        items: string
    inputBinding:
      valueFrom: replacementValue


  - id: args.py
    type: File
    default:
      class: File
      location: args.py
    inputBinding:
      position: -1

outputs:
  - id: args
    type: string[]
baseCommand: python