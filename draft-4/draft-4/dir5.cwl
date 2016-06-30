class: CommandLineTool
cwlVersion: draft-4.dev3
requirements:
  - class: ShellCommandRequirement
  - class: InitialWorkDirRequirement
    listing: $(inputs.indir.listing)
inputs:
  indir: Directory
outputs:
  outlist:
    type: File
    outputBinding:
      glob: output.txt
baseCommand: []
arguments: ["find", ".",
  {shellQuote: false, valueFrom: "|"},
  "sort"]
stdout: output.txt