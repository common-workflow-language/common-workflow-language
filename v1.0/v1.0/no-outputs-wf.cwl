#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0
doc: "Workflow without outputs."
inputs:
  file1: File
outputs: []
steps:
  step0:
    in: {file1: file1}
    out: []
    run: 
      class: CommandLineTool
      cwlVersion: v1.0
      doc: "CommandLineTool without outputs."
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