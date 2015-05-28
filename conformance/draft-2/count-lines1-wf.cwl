#!/usr/bin/env cwl-runner
class: Workflow

inputs:
  - { id: "#file1", datatype: File }

outputs:
  - { id: "#count_output", datatype: int, connect: {"source": "#step2_output"} }

steps:
  - run: {id: wc-tool.cwl}
    inputs:
      - {param: "wc-tool.cwl#file1", connect: {source: "#file1"}}
    outputs:
      - {id: "#step1_output", param: "wc-tool.cwl#output"}

  - run: {id: parseInt-tool.cwl}
    inputs:
      - {param: "parseInt-tool.cwl#file1", connect: {source: "#step1_output"}}
    outputs:
      - {id: "#step2_output", param: "parseInt-tool.cwl#output"}
