#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs:
  bar:
    type: Any

outputs:
  t1:
    type: Any
    outputSource: step1/t1

steps:
  step1:
    in:
      bar: bar
    out: [t1]
    run: io-any-1.cwl
