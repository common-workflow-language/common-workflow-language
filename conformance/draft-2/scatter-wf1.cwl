#!/usr/bin/env cwl-runner

class: Workflow
inputs:
  - id: "#inp"
    type:
      type: array
      items: string
requirements:
  - class: ScatterFeatureRequirement
steps:
  - id: "#step1"
    inputs:
      - {id: "#step1.echo_in", source: "#inp"}
    outputs:
      - id: "#step1.echo_out"
    scatter: "#step1.echo_in"
    run:
      class: CommandLineTool
      inputs:
        - id: "#echo_in"
          type: string
          inputBinding: {}
      outputs:
        - id: "#echo_out"
          type: string
          outputBinding:
            glob: "step1_out"
            loadContents: true
            outputEval:
              engine: "cwl:JsonPointer"
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
    source: "#step1.echo_out"