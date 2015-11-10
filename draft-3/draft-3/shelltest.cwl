class: CommandLineTool
description: "Reverse each line using the `rev` command then sort."
requirements:
  - class: ShellCommandRequirement
inputs:
  - id: "#input"
    type: File
outputs:
  - id: "#output"
    type: File
    outputBinding:
      glob: output.txt

baseCommand: []
arguments:
  - rev
  - valueFrom:
      engine: cwl:JsonPointer
      script: /job/input
  - valueFrom: " | "
    shellQuote: false
  - sort
  - valueFrom: "> output.txt"
    shellQuote: false
