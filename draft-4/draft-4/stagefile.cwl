class: CommandLineTool
cwlVersion: draft-4.dev3
requirements:
  InitialWorkDirRequirement:
    listing:
      - entryname: $(inputs.infile.basename)
        entry: $(inputs.infile)
        writable: true
inputs:
  infile: File
outputs:
  outfile:
    type: File
    outputBinding:
      glob: $(inputs.infile.basename)
baseCommand: "sed"
arguments: ["-i", "s/Ishmael/Bob/", $(inputs.infile.basename)]
