#!/usr/bin/env cwl-runner

class: ExpressionTool
cwlVersion: "cwl:draft-3.dev2"

inputs:
  - { id: file1, type: File, inputBinding: { loadContents: true } }

outputs:
  - { id: output, type: int }

expression: >
  ${return {'output': parseInt($job.file1.contents)};}
