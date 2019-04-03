#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
inputs: []
outputs:
  out: stdout

hints:
- $import: envvar.yml

baseCommand: ["echo", "$TEST_ENV"]

stdout: out
