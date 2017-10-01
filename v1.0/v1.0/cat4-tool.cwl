#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: "Print the contents of a file to stdout using 'cat' running in a docker container."
hints:
  DockerRequirement:
    dockerPull: debian:stretch-slim
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
