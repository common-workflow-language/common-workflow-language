#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0
doc: "Workflow without inputs."
inputs: []
outputs: 
  output:
    type: File
    outputSource: step0/output
steps:
  step0:
    in: []
    out: [output]
    run: 
      class: CommandLineTool
      cwlVersion: v1.0
      doc: "CommandLineTool without inputs."
      hints:
        DockerRequirement:
          dockerPull: debian:stretch-slim
      inputs: []
      outputs:
        output:
          type: File
          outputBinding: { glob: output }
      baseCommand: [echo, cwl]
      stdout: output
