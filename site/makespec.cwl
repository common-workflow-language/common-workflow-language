cwlVersion: v1.0
class: Workflow

inputs:
  schema_in: string
  context_target: string
  rdfs_target: string

outputs:
  index_out:
    type: File
    source: "#doc/out"

  - id: context_out
    type: File
    source: "#context/out"

  - id: rdfs_out
    type: File
    source: "#rdfs/out"

steps:
  - id: context
    run: "makecontext.cwl#makecontext"
    inputs:
      - { id: schema, source: "#schema_in" }
      - { id: target, source: "#context_target"}
    outputs:
      - { id: out}

  - id: rdfs
    run: "makecontext.cwl#makerdfs"
    inputs:
      - { id: schema, source: "#schema_in" }
      - { id: target, source: "#rdfs_target"}
    outputs:
      - { id: out}
