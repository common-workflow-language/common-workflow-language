cwlVersion: v1.1.0-dev1
class: CommandLineTool
inputs:
  dependent_parameters:
    type:
      type: record
      name: dependent_parameters
      fields:
        itemA:
          type: string
          inputBinding:
            prefix: -A
        itemB:
          type: string
          inputBinding:
            prefix: -B
  exclusive_parameters:
    type:
      - type: record
        name: itemC
        fields:
          itemC:
            type: string
            inputBinding:
              prefix: -C
      - type: record
        name: itemD
        fields:
          itemD:
            type: string
            inputBinding:
              prefix: -D
outputs: []
baseCommand: echo
