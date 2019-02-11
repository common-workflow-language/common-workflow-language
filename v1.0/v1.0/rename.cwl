class: CommandLineTool
cwlVersion: v1.0
baseCommand: "true"
hints:
  ResourceRequirement:
    ramMin: 8
requirements:
  InitialWorkDirRequirement:
    listing:
      - entryname: $(inputs.newname)
        entry: $(inputs.srcfile)
inputs:
  srcfile: File
  newname: string
outputs:
  outfile:
    type: File
    outputBinding:
      glob: $(inputs.newname)
