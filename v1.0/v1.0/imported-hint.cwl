#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
  ShellCommandRequirement: {}
inputs: []
outputs:
  out: stdout

hints:
- $import: envvar.yml

arguments:
  - valueFrom: "/bin/sh"
    position: 1
    shellQuote: false
  - valueFrom: "-c"
    position: 2
    shellQuote: false
  - valueFrom: "echo $TEST_ENV"
    position: 3
    shellQuote: true

stdout: out
