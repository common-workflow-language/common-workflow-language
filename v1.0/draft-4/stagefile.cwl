class: CommandLineTool
cwlVersion: v1.0.dev4
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
