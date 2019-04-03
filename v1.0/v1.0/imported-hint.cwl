#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool

requirements:
  ShellCommandRequirement: {}
  ResourceRequirement:
    ramMin: 8
inputs: []
outputs:
  out:
    type: File
    outputBinding:
      glob: out

hints:
- $import: envvar.yml

arguments:
  - valueFrom: "echo $TEST_ENV > out"
    position: 3
    shellQuote: false