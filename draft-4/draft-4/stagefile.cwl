class: CommandLineTool
cwlVersion: draft-4.dev3
requirements:
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.infile)
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
