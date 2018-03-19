#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

requirements:
  ResourceRequirement:
      coresMin: 4
      coresMax: 4

inputs: []

steps:
  step1:
    requirements:
      ResourceRequirement:
          coresMin: 1
          coresMax: 1
    run:
      class: CommandLineTool
      inputs: []
      outputs:
        output:
          type: stdout
      baseCommand: echo
      stdout: cores.txt
      arguments: [ $(runtime.cores) ]
    in: []
    out: [output]

outputs:
  out:
    type: File
    outputSource: step1/output
