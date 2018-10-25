#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  SchemaDefRequirement:
    types:
      - $import: capture_kit.yml

inputs:
  bam: string
  capture_kit: capture_kit.yml#capture_kit

outputs:
  output_bam:
    type: File
    outputSource: touch_bam/empty_file

steps:
  touch_bam:
    run: touch.cwl
    in:
      name: bam
    out: [ empty_file ]
