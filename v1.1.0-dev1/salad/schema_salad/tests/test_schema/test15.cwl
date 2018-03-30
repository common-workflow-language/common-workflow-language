#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  message:
    type: string
    inputBinding:
      position: 1
      invalid_field: it_is_invalid_field
      another_invalid_field: invalid
outputs: []
