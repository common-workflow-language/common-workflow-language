#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow
inputs: []
outputs:
  runtime_review:
    type: File
    outputSource: evaluate_runtime/runtime_review
steps:
  record_runtime:
    run:
      class: CommandLineTool
      baseCommand: echo
      inputs: []
      arguments:
       - '{"runtime":$(runtime)}'
      stdout: runtime.json
      outputs:
        runtime: stdout
    in: []
    out: [runtime]
  evaluate_runtime:
    run:
      class: CommandLineTool
      hints:
        DockerRequirement:
          dockerPull: everpeace/curl-jq
      inputs:
        runtime:
          type: File
          inputBinding:
            position: 2
      stdout: runtime_review.txt
      outputs:
        runtime_review: stdout
      baseCommand: jq
      arguments:
       - valueFrom: |
          .runtime | has("cores"), has("outdir"), has("outdirSize"), has("ram"), has("tmpdir"), has("tmpdirSize")
         position: 1
    in: { runtime: record_runtime/runtime }
    out: [ runtime_review ]
      

