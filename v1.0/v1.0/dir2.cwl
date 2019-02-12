class: CommandLineTool
cwlVersion: v1.0
requirements:
  ShellCommandRequirement: {}
hints:
  DockerRequirement:
    dockerPull: debian:stretch-slim
  ResourceRequirement:
    ramMin: 8
inputs:
  indir: Directory
outputs:
  outlist:
    type: File
    outputBinding:
      glob: output.txt
arguments: ["cd", "$(inputs.indir.path)",
  {shellQuote: false, valueFrom: "&&"},
  "find", ".",
  {shellQuote: false, valueFrom: "|"},
  "sort"]
stdout: output.txt
