#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0
doc: "Workflow without outputs."
inputs:
  file1: File
outputs: []
steps:
  step0:
    in: {file1: file1}
    out: []
    run: no_outputs_tool.cwl
