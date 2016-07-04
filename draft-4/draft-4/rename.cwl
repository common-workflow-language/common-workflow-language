class: CommandLineTool
cwlVersion: cwl:draft-4.dev3
baseCommand: "true"
requirements:
  InitialWorkDirRequirement:
    listing:
      $(inputs.newname): $(inputs.srcfile.location)
inputs:
  srcfile: File
  newname: string
outputs:
  outfile:
    type: File
    outputBinding:
      glob: $(inputs.newname)
