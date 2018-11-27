#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: "Print the contents of a file to stdout using 'cat' running in a docker container."
hints:
  DockerRequirement:
    dockerPull: debian:stretch-slim
inputs:
  file1:
    type: File
    label: Input File
    inputBinding: {position: 1}
outputs: []
baseCommand: echo
