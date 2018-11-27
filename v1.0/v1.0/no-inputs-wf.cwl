#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0
inputs: []
outputs: 
  output:
    type: File
    outputSource: step0/output
steps:
  step0:
    in: []
    out: [output]
    run: no_inputs_tool.cwl
