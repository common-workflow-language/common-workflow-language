#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0

inputs:
  dir1: Directory

outputs:
  output:
    type: stdout

baseCommand: [cat]

stdin: $(inputs.dir1.listing[0].path)
