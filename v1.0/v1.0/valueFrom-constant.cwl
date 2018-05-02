class: CommandLineTool
cwlVersion: v1.0

hints:
  - class: DockerRequirement
    dockerPull: python:2-slim

inputs:
  - id: array_input
    type:
      - type: array
        items: File
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
