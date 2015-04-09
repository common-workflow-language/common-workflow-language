#!/usr/bin/env cwl-runner

class: Workflow
inputs:
  - id: "#inp1"
    type:
      type: array
      items: string
  - id: "#inp2"
    type:
      type: array
      items: string
steps:
  - id: "#step1"
    class: CommandLineTool
    scatter: ["#step1_in1", "#step1_in2"]
    scatterMethod: nested_crossproduct
    inputs:
      - id: "#step1_in1"
        type: string
        connect: {source: "#inp1"}
        commandLineBinding: {}
      - id: "#step1_in2"
        type: string
        connect: {source: "#inp2"}
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
    connect: {source: "#step1_out"}
    type:
      type: array
      items:
        type: array
        items: string
