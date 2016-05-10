#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-4.dev1
class: Workflow
inputs:
  inp:
    type:
      type: array
      items: string
outputs:
  out:
    type:
      type: array
      items: string
    source: "#step1/echo_out"

requirements:
  - class: ScatterFeatureRequirement

steps:
  - id: step1
    in:
      echo_in: "#inp"
    out: [echo_out]
    scatter: "#step1/echo_in"
    run:
      class: CommandLineTool
      inputs:
        echo_in:
          type: string
          inputBinding: {}
      outputs:
        echo_out:
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
