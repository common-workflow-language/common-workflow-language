class: CommandLineTool
cwlVersion: v1.1.0-dev1
hints:
  DockerRequirement:
    dockerPull: debian:stretch-slim
  ShellCommandRequirement: {}
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