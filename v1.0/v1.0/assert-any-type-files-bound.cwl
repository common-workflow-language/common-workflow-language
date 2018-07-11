#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0
inputs:
  in:
    type: Any
    inputBinding: {}
outputs: []
arguments:
  - ls
  - $(inputs.in)
