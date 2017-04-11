#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow
inputs:
  inp: string[]
outputs:
  out:
    type: string[]
    outputSource: step1/echo_out

requirements:
  - class: ScatterFeatureRequirement

steps:
  step1:
    in:
      echo_in: inp
    out: [echo_out]
    scatter: echo_in
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
