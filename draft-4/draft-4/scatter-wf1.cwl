#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
class: Workflow
inputs:
  - id: inp
    type:
      type: array
      items: string
outputs:
  - id: out
    type:
      type: array
      items: string
    source: "#step1/echo_out"

requirements:
  - class: ScatterFeatureRequirement

steps:
  - id: step1
    inputs:
      - {id: echo_in, source: "#inp"}
    outputs:
      - id: echo_out
    scatter: "#step1/echo_in"
    run:
      class: CommandLineTool
      inputs:
        - id: echo_in
          type: string
          inputBinding: {}
      outputs:
        - id: echo_out
          type: string
          outputBinding:
            glob: "step1_out"
            loadContents: true
            outputEval: $(self[0].contents)
      baseCommand: "echo"
      arguments:
        - "-n"
        - "foo"
      stdout: "step1_out"
