#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow
inputs: []
outputs:
  self_review:
    type: File
    outputSource: evaluate_self/self_review
steps:
  dump_self:
    run:
      class: CommandLineTool
      baseCommand: echo
      inputs: []
      arguments:
       - '{"self":$(self)}'
      stdout: self.json
      outputs:
        self_json: stdout
    in: []
    out: [self_json]
  evaluate_self:
    run:
      class: CommandLineTool
      hints:
        DockerRequirement:
          dockerPull: everpeace/curl-jq
      inputs:
        self:
          type: File
          inputBinding:
            position: 2
      stdout: self_review.txt
      outputs:
        self_review: stdout
      baseCommand: jq
      arguments:
       - valueFrom: '.self | type == "null"'
         position: 1
    in: { self: dump_self/self_json }
    out: [ self_review ]
      

