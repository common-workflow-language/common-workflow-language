#!/usr/bin/env cwl-runner
cwlVersion: cwl:v1.0

class: Workflow
inputs:
  render:
    type:
      type: array
      items:
        type: record
        fields:
          source: File
          renderlist: string[]?
          redirect: string[]?
          target: string
          brandlink: string
          brandimg: string
          primtype: string?
          extra: File
  schemas:
    type:
      type: array
      items:
        type: record
        fields:
          schema_in: File
          context_target: string
          rdfs_target: string
  brandimg: File
  empty:
    type: string?
    default: ""

outputs:
  doc_out:
    type: File
    outputSource: merge/dir
  report:
    type: File
    outputSource: generate_report/out

requirements:
  - class: ScatterFeatureRequirement
  - class: StepInputExpressionRequirement
  - class: SubworkflowFeatureRequirement
  - class: MultipleInputFeatureRequirement
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: commonworkflowlanguage/cwltool_module

steps:
  rdfs:
    scatter: schemas
    in:
      schemas: schemas
      schema: { valueFrom: $(inputs.schemas.schema_in) }
      target: { valueFrom: $(inputs.schemas.rdfs_target) }
    out: [out, targetdir]
    run: makerdfs.cwl

  context:
    scatter: schemas
    in:
      schemas: schemas
      schema: { valueFrom: $(inputs.schemas.schema_in) }
      target: { valueFrom: $(inputs.schemas.context_target) }
    out: [out, targetdir]
    run: makecontext.cwl

  docs:
    scatter: render
    in:
      render: render
      source: { valueFrom: $(inputs.render.source) }
      target: { valueFrom: $(inputs.render.target) }
      renderlist: { valueFrom: $(inputs.render.renderlist) }
      redirect: { valueFrom: $(inputs.render.redirect) }
      brandlink: { valueFrom: $(inputs.render.brandlink) }
      brand: { valueFrom: $(inputs.render.brandimg) }
      primtype: { valueFrom: $(inputs.render.primtype) }
      extra: { valueFrom: $(inputs.render.extra) }
    out: [out, targetdir, extra_out]
    run:  makedoc.cwl

  merge:
    in:
      primary:
        source: docs/out
        valueFrom: $(self[0])
      secondary:
        source: [docs/out, rdfs/out, context/out, brandimg, docs/extra_out]
        linkMerge: merge_flattened
        valueFrom: $(self.slice(1))
      dirs:
        source: [docs/targetdir, rdfs/targetdir, context/targetdir, empty, docs/targetdir]
        linkMerge: merge_flattened
        valueFrom: $(self.slice(1))
    out: [dir]
    run: mergesecondary.cwl

  generate_report:
    in:
      inp: merge/dir
      target: { default: "linkchecker-report.txt"}
    out: [out]
    run: linkchecker.cwl
