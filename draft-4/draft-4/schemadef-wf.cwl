#!/usr/bin/env cwl-runner

cwlVersion: cwl:v1.0.dev4
class: Workflow

requirements:
  - $import: schemadef-type.yml

inputs:
  hello: "schemadef-type.yml#HelloType"

outputs:
  output:
    type: File
    outputSource: step1/output

steps:
  step1:
    in:
      hello: hello
    out: [output]
    run: schemadef-tool.cwl
