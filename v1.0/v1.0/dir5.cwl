class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8
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
arguments: ["find", "-L", ".", "!", "-path", "*.txt",
  {shellQuote: false, valueFrom: "|"},
  "sort"]
stdout: output.txt
