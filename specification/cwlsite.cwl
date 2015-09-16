#!/usr/bin/env cwl-runner
cwlVersion: "cwl:draft-3.dev1"

class: Workflow
inputs:
  - {id: index_in, type: File}
  - {id: index_target, type: string}
  - {id: title, type: string}

  - id: index_strip_lines
    type: int
    default: 3

  - id: schema_in
    type: { type: array, items: File }

  - id: schema_target
    type: { type: array, items: string }

  - id: context_target
    type: { type: array, items: string }

  - id: rdfs_target
    type: { type: array, items: string }

outputs:
  - id: readme_out
    type: File
    source: "#readme/out"
  - id: index
    type: { type: array, items: File }
    source: "#spec/index_out"
  - id: context
    type: { type: array, items: File }
    source: "#spec/context_out"
  - id: rdfs
    type: { type: array, items: File }
    source: "#spec/rdfs_out"

requirements:
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement

hints:
  - class: DockerRequirement
    dockerPull: commonworkflowlanguage/cwltool_module

steps:
  - id: spec
    inputs:
      - {id: schema_in, source: "#schema_in" }
      - {id: schema_target, source: "#schema_target" }
      - {id: context_target, source: "#context_target" }
      - {id: rdfs_target, source: "#rdfs_target" }

    outputs:
      - { id: index_out }
      - { id: context_out }
      - { id: rdfs_out }

    scatter:
      - "#spec/schema_in"
      - "#spec/schema_target"
      - "#spec/context_target"
      - "#spec/rdfs_target"

    scatterMethod: dotproduct

    run: {"@import": "makespec.cwl"}

  - id: strip_lines
    inputs:
      - { id: strip_leading_lines_in, source: "#index_in" }
      - { id: strip_leading_lines_count, source: "#index_strip_lines" }
    outputs:
      - { id: strip_leading_lines_out }
    run:  {"@import": "strip.cwl"}

  - id: readme
    inputs:
      - { id: source, source: "#strip_lines/strip_leading_lines_out" }
      - { id: target, source: "#index_target" }
      - { id: title, source: "#title" }
    outputs:
      - { id: out }
    run:  {"@import": "makedoc.cwl"}
