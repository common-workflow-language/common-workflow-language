class: CommandLineTool
cwlVersion: cwl:draft-4.dev2
baseCommand: "true"
requirements:
  CreateFileRequirement:
    fileDef:
      - filename: $(inputs.newname)
        fileContent: $(inputs.srcfile)
inputs:
  srcfile: File
  newname: string
outputs:
  outfile:
    type: File
    outputBinding:
      glob: $(inputs.newname)
