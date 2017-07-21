class: CommandLineTool
cwlVersion: v1.0
requirements:
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.file1)
        entryname: bob.txt
  ShellCommandRequirement: {}
inputs:
  file1: File
outputs: []
arguments:
  - shellQuote: false
    valueFrom: |
      test "$(inputs.file1.path)" = "$(runtime.outdir)/bob.txt"
