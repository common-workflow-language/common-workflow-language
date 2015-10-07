#!/usr/bin/env cwl-runner

class: ExpressionTool

requirements:
  - import: node-engine.cwl

inputs:
  - { id: "#file1", type: File, inputBinding: { loadContents: true } }

outputs:
  - { id: "#output", type: int }

expression:
  engine: node-engine.cwl
  script: "{return {'output': parseInt($job.file1.contents)};}"
