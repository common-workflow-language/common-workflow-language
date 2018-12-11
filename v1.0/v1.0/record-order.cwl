class: CommandLineTool
cwlVersion: v1.0
baseCommand: python
inputs:
  - id: args.py
    type: File
    default:
      class: File
      location: args.py
    inputBinding:
      position: -1
  - id: a
    type:
      type: record
      fields:
        - name: b
          type: int
          inputBinding:
            position: 1
            prefix: -b
        - name: c
          type: int
          inputBinding:
            position: 3
            prefix: -c
    inputBinding:
      position: 5
      prefix: -a
  - id: d
    type:
      type: record
      fields:
        - name: e
          type: int
          inputBinding:
            position: 2
            prefix: -e
        - name: f
          type: int
          inputBinding:
            position: 4
            prefix: -f
    inputBinding:
      position: 6
      prefix: -d
outputs:
  - id: args
    type:
      type: array
      items: string

hints:
  - class: DockerRequirement
    dockerPull: python:2-slim
