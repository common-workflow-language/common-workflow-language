class: CommandLineTool
cwlVersion: cwl:draft-4.dev1

inputs:
  ids:
    type:
      type: array
      items: string
    inputBinding:
      position: 1

outputs:
  files:
    type:
      type: array
      items: File
    outputBinding:
      glob: $(inputs.ids)

baseCommand: touch
