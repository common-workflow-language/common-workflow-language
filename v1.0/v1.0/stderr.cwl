#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: "Test of capturing stderr output."
hints:
  ResourceRequirement:
    ramMin: 8
requirements:
  ShellCommandRequirement: {}
inputs: []
outputs:
  output_file:
    type: File
    outputBinding: {glob: error.txt}
arguments:
 - { valueFrom: "echo foo 1>&2", shellQuote: False }
stderr: error.txt
