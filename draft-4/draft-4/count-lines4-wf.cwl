#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-4.dev1

inputs:
    file1:
      type: File
    file2:
      type: File

outputs:
    count_output:
      type: {type: array, items: int}
      source: "#step1/output"

requirements:
  - class: ScatterFeatureRequirement
  - class: MultipleInputFeatureRequirement

steps:
  step1:
    run: wc2-tool.cwl
    scatter: "#step1/file1"
    in:
      file1: ["#file1", "#file2"]
    out: [output]
