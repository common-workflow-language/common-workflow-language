class: Workflow

inputs:
  - id: "#schema_in"
    type: File
  - id: "#schema_target"
    type: string
  - id: "#context_target"
    type: string
  - id: "#rdfs_target"
    type: string

outputs:
  - id: "#index_out"
    type: File
    source: "#doc.makedoc_out"
  - id: "#context_out"
    type: File
    source: "#context.makecontext_out"
  - id: "#rdfs_out"
    type: File
    source: "#rdfs.makerdfs_out"

steps:
  - id: "#doc"
    run: {import: "makedoc.cwl"}
    inputs:
      - { id: "#doc.makedoc_source", source: "#schema_in" }
      - { id: "#doc.makedoc_target", source: "#schema_target" }
    outputs:
      - { id: "#doc.makedoc_out" }

  - id: "#context"
    run: {import: "makecontext.cwl#makecontext"}
    inputs:
      - { id: "#context.makecontext_target", source: "#context_target"}
    outputs:
      - { id: "#context.makecontext_out"}

  - id: "#rdfs"
    run: {import: "makecontext.cwl#makerdfs"}
    inputs:
      - { id: "#rdfs.makerdfs_target", source: "#rdfs_target"}
    outputs:
      - { id: "#rdfs.makerdfs_out"}
