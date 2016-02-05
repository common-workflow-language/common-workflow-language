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
              type: array
              items: string
          - name: redirect
            type:
              type: array
              items: string
          - name: target
            type: string
          - name: brandlink
            type: string

  - id: schemas
    type:
      type: array
      items:
        name: rdfs
        type: record
        fields:
          - name: schema_in
            type: File
          - name: context_target
            type: string
          - name: rdfs_target
            type: string
  - id: brand
    type: string

outputs:
  - id: doc_out
    type:
      type: array
      items: File
    source: "#docs/out"
  - id: report
    type: File
    source: "#report/out"
  - id: context
    type:
      type: array
      items: File
    source: "#context/out"
  - id: rdfs
    type:
      type: array
      items: File
    source: "#rdfs/out"

requirements:
  - class: ScatterFeatureRequirement
  - class: StepInputExpressionRequirement
  - class: SubworkflowFeatureRequirement

hints:
  - class: DockerRequirement
    dockerPull: commonworkflowlanguage/cwltool_module

steps:
  - id: rdfs
    inputs:
      - {id: schema, source: "#schemas", valueFrom: $(self.schema_in) }
      - {id: target, source: "#schemas", valueFrom: $(self.rdfs_target) }
    outputs:
      - { id: out }
    scatter: ["#rdfs/schema", "#rdfs/target"]
    scatterMethod: dotproduct
    run: makerdfs.cwl

  - id: context
    inputs:
      - {id: schema, source: "#schemas", valueFrom: $(self.schema_in) }
      - {id: target, source: "#schemas", valueFrom: $(self.context_target) }
    outputs:
      - { id: out }
    scatter: ["#context/schema", "#context/target"]
    scatterMethod: dotproduct
    run: makecontext.cwl

  - id: docs
    inputs:
      - { id: source, source: "#render", valueFrom: $(self.source) }
      - { id: target, source: "#render", valueFrom: $(self.target) }
      - { id: renderlist, source: "#render", valueFrom: $(self.renderlist) }
      - { id: redirect, source: "#render", valueFrom: $(self.redirect) }
      - { id: brandlink, source: "#render", valueFrom: $(self.brandlink) }
      - { id: primtype, source: "#render", valueFrom: $(self.primtype) }
      - { id: brand, source: "#brand" }
    outputs:
      - { id: out }
    scatter: ["#docs/source", "#docs/target", "#docs/renderlist",
      "#docs/redirect", "#docs/brandlink", "#docs/primtype"]
    scatterMethod: dotproduct
    run:  makedoc.cwl

  - id: report
    inputs:
      - {id: inp, source: "#docs/out"}
      - {id: target, default: "linkchecker-report.txt"}
    outputs:
      - id: out
    run: linkchecker.cwl
