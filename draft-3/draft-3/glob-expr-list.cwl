class: CommandLineTool
cwlVersion: cwl:draft-3

inputs:
  - id: ids
    type:
      type: array
      items: string
    inputBinding:
      position: 1

outputs:
  - id: files
    type:
      type: array
      items: File
    outputBinding:
      glob: $(inputs.ids)

baseCommand: touch
