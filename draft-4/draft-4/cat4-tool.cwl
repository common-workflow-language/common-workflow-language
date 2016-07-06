#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: cwl:v1.0.dev4
description: "Print the contents of a file to stdout using 'cat' running in a docker container."
hints:
  DockerRequirement:
    dockerPull: debian:wheezy
inputs:
  file1: File
outputs:
  output_txt:
    type: File
    outputBinding:
      glob: output.txt
baseCommand: cat
stdout: output.txt
stdin: $(inputs.file1.path)
