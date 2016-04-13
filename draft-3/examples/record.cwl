cwlVersion: cwl:draft-3
class: CommandLineTool
inputs:
  - id: dependent_parameters
    type:
      type: record
      name: dependent_parameters
      fields:
        - name: itemA
          type: string
          inputBinding:
            prefix: -A
        - name: itemB
          type: string
          inputBinding:
            prefix: -B
  - id: exclusive_parameters
    type:
      - type: record
        name: itemC
        fields:
          - name: itemC
            type: string
            inputBinding:
              prefix: -C
      - type: record
        name: itemD
        fields:
          - name: itemD
            type: string
            inputBinding:
              prefix: -D
outputs: []
baseCommand: echo
