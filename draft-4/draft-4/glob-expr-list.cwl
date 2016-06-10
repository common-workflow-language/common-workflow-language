class: CommandLineTool
cwlVersion: cwl:draft-4.dev2

inputs:
  ids:
    type: string[]
    inputBinding:
      position: 1

outputs:
  files:
    type: File[]
    outputBinding:
      glob: $(inputs.ids)

baseCommand: touch
