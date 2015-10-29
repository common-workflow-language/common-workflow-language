#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3.dev1"
class: Workflow

requirements:
  - "@import": schemadef-type.yml

inputs:
    - id: "#hello"
      type: "schemadef-type.yml#HelloType"
outputs:
    - id: "#output"
      type: File
      source: "#step1.output"

steps:
  - id: "#step1"
    inputs:
      - { id: "#step1.hello", source: "#hello" }
    outputs:
      - { id: "#step1.output" }
    run: { "@import": schemadef-tool.cwl }