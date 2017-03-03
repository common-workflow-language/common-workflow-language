class: CommandLineTool
cwlVersion: v1.1.0-dev1
requirements:
  - class: ShellCommandRequirement
inputs:
  inf: File
outputs:
  outlist:
    type: File
    outputBinding:
      glob: output.txt
arguments: ["cd", "$(inputs.inf.dirname)/xtestdir",
  {shellQuote: false, valueFrom: "&&"},
  "find", ".",
  {shellQuote: false, valueFrom: "|"},
  "sort"]
stdout: output.txt
