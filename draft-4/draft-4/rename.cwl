class: CommandLineTool
cwlVersion: cwl:draft-4.dev1
baseCommand: "true"
requirements:
  CreateFileRequirement:
    fileDef:
      - filename: $(inputs.newname)
        fileContent: $(inputs.srcfile)
inputs:
  srcfile:
    type: File
  newname:
    type: string
outputs:
  outfile:
    type: File
    outputBinding:
      glob: $(inputs.newname)
