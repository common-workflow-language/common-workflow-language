#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: "CommandLineTool without outputs."
hints:
  DockerRequirement:
    dockerPull: debian:stretch-slim
  ResourceRequirement:
    ramMin: 8
inputs:
  file1:
    type: File
    label: Input File
    inputBinding: {position: 1}
outputs: []
baseCommand: echo
