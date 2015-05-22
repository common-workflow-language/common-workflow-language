#!/usr/bin/env cwl-runner

class: Workflow
inputs:
  - id: "#inp"
    type:
      type: array
      items: string
steps:
  - id: "#step1"
    class: CommandLineTool
    requirements:
      - class: Scatter
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
          glob: "step1_out"
          loadContents: true
          outputEval:
            class: Expression
            engine: JsonPointer
            script: "context/0/contents"
    baseCommand: "echo"
    arguments:
      - "-n"
      - "foo"
    stdout: "step1_out"
outputs:
  - id: "#out"
    type:
      type: array
      items: string
    connect: {source: "#step1_out"}