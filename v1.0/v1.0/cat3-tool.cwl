#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: "Print the contents of a file to stdout using 'cat' running in a docker container."
hints:
  DockerRequirement:
    dockerPull: debian:stretch-slim
  ResourceRequirement:
    ramMin: 8
inputs:
  file1:
    type: File
    label: Input File
    doc: "The file that will be copied using 'cat'"
    inputBinding: {position: 1}
outputs:
  output_file:
    type: File
    outputBinding: {glob: output.txt}
baseCommand: cat
stdout: output.txt
