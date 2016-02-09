class: CommandLineTool
cwlVersion: cwl:draft-3
description: "Reverse each line using the `rev` command then sort."
requirements:
  - class: ShellCommandRequirement
inputs:
  - id: input
    type: File
outputs:
  - id: output
    type: File
    outputBinding:
      glob: output.txt

baseCommand: []
arguments:
  - rev
  - {valueFrom: $(inputs.input)}
  - {valueFrom: " | ", shellQuote: false}
  - sort
  - {valueFrom: "> output.txt", shellQuote: false}
