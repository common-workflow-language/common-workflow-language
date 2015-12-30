#!/usr/bin/env cwl-runner
cwlVersion: "cwl:draft-3.dev4"

class: Workflow
inputs:
  - id: render
    type:
      type: array
      items:
        name: render
        type: record
        fields:
          - name: source
            type: File
          - name: renderlist
            type:
              - type: array
                items: string
          - name: target
            type: string

  - id: schema_in
    type: File
  - id: context_target
    type: string
  - id: rdfs_target
    type: string

outputs:
  - id: doc_out
    type:
      type: array
      items: File
    source: "#docs/out"
  - id: context
    type: File
    source: "#context/out"
  - id: rdfs
    type: File
    source: "#rdfs/out"

requirements:
  - class: ScatterFeatureRequirement

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

  - id: docs
    inputs:
      - { id: source, source: "#render", valueFrom: $(self.source) }
      - { id: target, source: "#render", valueFrom: $(self.target) }
      - { id: renderlist, source: "#render", valueFrom: $(self.renderlist) }
    outputs:
      - { id: out }
    scatter: ["#docs/source", "#docs/target", "#docs/renderlist"]
    scatterMethod: dotproduct
    run:  makedoc.cwl
