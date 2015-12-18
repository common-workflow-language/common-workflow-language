#!/usr/bin/env cwl-runner
cwlVersion: "cwl:draft-3.dev4"

class: Workflow
inputs:
  - id: readme_in
    type: File
  - id: readme_target
    type: string
  - id: schema_in
    type: File
  - id: context_target
    type: string
  - id: rdfs_target
    type: string
  - id: spec_target
    type: string
  - id: spec_renderlist
    type:
      type: array
      items: string

outputs:
  - id: readme_out
    type: File
    source: "#readme/out"
  - id: index
    type: File
    source: "#draft3spec/out"
  - id: context
    type: File
    source: "#context/out"
  - id: rdfs
    type: File
    source: "#rdfs/out"

requirements:
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement

hints:
  - class: DockerRequirement
    dockerPull: commonworkflowlanguage/cwltool_module

steps:
  - id: rdfs
    inputs:
      - {id: schema, source: "#schema_in" }
      - {id: target, source: "#rdfs_target" }
    outputs:
      - { id: out }
    run: makerdfs.cwl

  - id: context
    inputs:
      - {id: schema, source: "#schema_in" }
      - {id: target, source: "#context_target" }
    outputs:
      - { id: out }
    run: makecontext.cwl

  - id: readme
    inputs:
      - { id: source, source: "#readme_in" }
      - { id: target, source: "#readme_target" }
    outputs:
      - { id: out }
    run:  makedoc.cwl

  - id: draft3spec
    inputs:
      - { id: source, source: "#schema_in" }
      - { id: target, source: "#spec_target" }
      - { id: renderlist, source: "#spec_renderlist" }
    outputs:
      - { id: out }
    run:  makedoc.cwl
