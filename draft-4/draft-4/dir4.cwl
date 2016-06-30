class: CommandLineTool
cwlVersion: draft-4.dev3
requirements:
  - class: ShellCommandRequirement
inputs:
  inf: File
outputs:
  outlist:
    type: File
    outputBinding:
      glob: output.txt
baseCommand: []
arguments: ["cd", "$(inputs.inf.dirname)",
  {shellQuote: false, valueFrom: "&&"},
  "find", ".",
  {shellQuote: false, valueFrom: "|"},
  "sort"]
stdout: output.txt