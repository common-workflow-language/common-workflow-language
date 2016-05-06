#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-4.dev1
requirements:
  - class: StepInputExpressionRequirement

inputs:
  in:
    type:
      name: in
      type: record
      fields:
        - name: file1
          type: File

outputs:
  count_output:
    type: int
    source: "#step2/output"

steps:
  step1:
    run: wc-tool.cwl
    in:
      file1:
        source: "#in"
        valueFrom: $(self.file1)
    out: [output]

  step2:
    run: parseInt-tool.cwl
    in:
      file1: "#step1/output"
    out: [output]
