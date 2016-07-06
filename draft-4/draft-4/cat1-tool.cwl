#!/usr/bin/env cwl-runner
cwlVersion: cwl:v1.0.dev4
class: CommandLineTool
description: "Print the contents of a file to stdout using 'cat' running in a docker container."
hints:
  DockerRequirement:
    dockerPull: debian:wheezy
  SoftwareRequirement:
    name: cat
inputs:
  file1:
    type: File
    inputBinding: {position: 1}
  numbering:
    type: boolean?
    inputBinding:
      position: 0
      prefix: -n
outputs: []
baseCommand: cat
