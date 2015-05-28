#!/usr/bin/env cwl-runner
"@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json"
class: Workflow
inputs:
    - { id: "#file1", type: File }

outputs:
    - { id: "#count_output", type: int, connect: {"source": "#step2_output"} }

requirements:
  - id: node-engine.cwl

steps:
  - id: "#step1"
    inputs:
      - { param: "#step1_file1", connect: {"source": "#file1"} }
    outputs:
      - { param: "#step1_output" }
    run:
      class: CommandLineTool
      inputs:
        - { id: "#step1_file1", type: File, inputBinding: {} }
      outputs:
        - { id: "#step1_output", type: File, outputBinding: { glob: output.txt } }
      stdout: output.txt
      baseCommand: ["wc"]

  - id: "#step2"
    inputs:
      - { "param": "#step2_file1", connect: {"source": "#step1_output"} }
    outputs:
      - { "param": "#step2_output" }
    run:
      class: ExpressionTool
      inputs:
        - { id: "#step2_file1", type: File, inputBinding: { loadContents: true } }
      outputs:
        - { id: "#step2_output", type: int }
      expression:
        engine: node-engine.cwl
        script: >
          {return {'step2_output': parseInt($job.step2_file1.contents)};}
