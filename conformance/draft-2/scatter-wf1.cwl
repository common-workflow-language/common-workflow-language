#!/usr/bin/env cwl-runner

class: Workflow
inputs:
  - id: "#inp"
    type:
      type: array
      items: string
requirements:
  - class: ScatterFeature
steps:
  - id: "#step1"
    class: CommandLineTool
    scatter: "#step1_in"
    inputs:
      - id: "#step1_in"
        type: string
        connect: {source: "#inp"}
        commandLineBinding: {}
    outputs:
      - id: "#step1_out"
        type: string
        outputBinding:
          loadContents: true
    baseCommand: "echo"
    arguments:
      - "-n"
      - "foo"
    stdout: {ref: "#step1_out"}
outputs:
  - id: "#out"
    type:
      type: array
      items: string
    connect: {source: "#step1_out"}