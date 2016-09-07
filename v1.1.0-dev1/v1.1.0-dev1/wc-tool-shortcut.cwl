#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.1.0-dev1

inputs:
  file1: stdin

outputs:
  output:
    type: File
    outputBinding: { glob: output }

baseCommand: [wc]

stdout: output
