#!/usr/bin/env cwl-runner

- id: "#main"
  class: Workflow
  inputs:
    - id: "#main_index_in"
      type: File
    - id: "#main_index_target"
      type: string
    - id: "#main_title"
      type: string
    - id: "#main_index_strip_lines"
      type: int
      default: 3

    - id: "#cwl_schema_in"
      type: { type: array, items: File }
    - id: "#cwl_schema_target"
      type: { type: array, items: string }
    - id: "#cwl_context_target"
      type: { type: array, items: string }
    - id: "#cwl_rdfs_target"
      type: { type: array, items: string }

  outputs:
    - id: "#main_index"
      type: File
      source: "#readme.makedoc_out"
    - id: "#spec_index"
      type: { type: array, items: File }
      source: "#spec.index_out"
    - id: "#spec_context"
      type: { type: array, items: File }
      source: "#spec.context_out"
    - id: "#spec_rdfs"
      type: { type: array, items: File }
      source: "#spec.rdfs_out"

  requirements:
    - class: ScatterFeatureRequirement
    - class: SubworkflowFeatureRequirement

  hints:
    - class: DockerRequirement
      dockerPull: commonworkflowlanguage/cwltool_module

  steps:
    - id: "#spec"
      inputs:
        - {id: "#spec.schema_in", source: "#cwl_schema_in" }
        - {id: "#spec.schema_target", source: "#cwl_schema_target" }
        - {id: "#spec.context_target", source: "#cwl_context_target" }
        - {id: "#spec.rdfs_target", source: "#cwl_rdfs_target" }

      outputs:
        - { id: "#spec.index_out" }
        - { id: "#spec.context_out" }
        - { id: "#spec.rdfs_out" }

      scatter:
        - "#spec.schema_in"
        - "#spec.schema_target"
        - "#spec.context_target"
        - "#spec.rdfs_target"

      scatterMethod: dotproduct

      run: {import: "makespec.cwl"}

    - id: "#strip_lines"
      inputs:
        - { id: "#strip_lines.strip_leading_lines_in", source: "#main_index_in" }
        - { id: "#strip_lines.strip_leading_lines_count", source: "#main_index_strip_lines" }
      outputs:
        - { id: "#strip_lines.strip_leading_lines_out" }
      run:  {import: "strip.cwl"}

    - id: "#readme"
      inputs:
        - { id: "#readme.makedoc_source", source: "#strip_lines.strip_leading_lines_out" }
        - { id: "#readme.makedoc_target", source: "#main_index_target" }
        - { id: "#readme.makedoc_title", source: "#main_title" }
      outputs:
        - { id: "#readme.makedoc_out" }
      run:  {import: "makedoc.cwl"}
