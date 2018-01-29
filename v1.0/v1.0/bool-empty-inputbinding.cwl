#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
inputs:
- id: flag
  type: boolean
  inputBinding: {}
- id: "args.py"
  type: File
  default:
    class: File
    location: args.py
  inputBinding:
    position: -1
outputs:
- id: args
  type: string[]
baseCommand: python
arguments: []