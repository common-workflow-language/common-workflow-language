#!/usr/bin/env cwl-runner
class: Workflow
inputs:
    - { id: "#file1", type: File }

outputs:
    - { id: "#count_output", type: int, source: "#step2.parseInt_output"}

requirements:
  - import: node-engine.cwl

steps:
  - id: "#step1"
    inputs:
      - { id: "#step1.wc_file1", source: "#file1" }
    outputs:
      - { id: "#step1.wc_output" }
    run:
      class: CommandLineTool
      inputs:
        - { id: "#wc_file1", type: File, inputBinding: {} }
      outputs:
        - { id: "#wc_output", type: File, outputBinding: { glob: output.txt } }
      stdout: output.txt
      baseCommand: ["wc"]

  - id: "#step2"
    inputs:
      - { "id": "#step2.parseInt_file1", source: "#step1.wc_output" }
    outputs:
      - { "id": "#step2.parseInt_output" }
    run:
      class: ExpressionTool
      inputs:
        - { id: "#parseInt_file1", type: File, inputBinding: { loadContents: true } }
      outputs:
        - { id: "#parseInt_output", type: int }
      expression:
        engine: node-engine.cwl
        script: >
          {return {'parseInt_output': parseInt($job.parseInt_file1.contents)};}
