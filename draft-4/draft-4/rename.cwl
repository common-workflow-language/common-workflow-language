class: CommandLineTool
cwlVersion: cwl:draft-4.dev3
baseCommand: "true"
requirements:
  InitialWorkDirRequirement:
    listing:
      - class: File
        basename: $(inputs.newname)
        location: $(inputs.srcfile.location)
inputs:
  srcfile: File
  newname: string
outputs:
  outfile:
    type: File
    outputBinding:
      glob: $(inputs.newname)
