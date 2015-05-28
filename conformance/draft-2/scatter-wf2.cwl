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
    requirements:
      - class: Scatter
        scatter: ["#step1_in1", "#step1_in2"]
        scatterMethod: nested_crossproduct
    inputs:
      - id: "#step1_in1"
        type: string
        connect: {source: "#inp1"}
        inputBinding: {}
      - id: "#step1_in2"
        type: string
        connect: {source: "#inp2"}
        inputBinding: {}
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
    stdout: step1_out
outputs:
  - id: "#out"
    connect: {source: "#step1_out"}
    type:
      type: array
      items:
        type: array
        items: string
