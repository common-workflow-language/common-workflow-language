cwlVersion: cwl:draft-3
class: Workflow
inputs:
  - id: inp
    type: File
  - id: ex
    type: string

outputs:
  - id: classout
    type: File
    source: "#compile/classfile"

steps:
  - id: untar
    run: tar-param.cwl
    inputs:
      - id: tarfile
        source: "#inp"
      - id: extractfile
        source: "#ex"
    outputs:
      - id: example_out

  - id: compile
    run: arguments.cwl
    inputs:
      - id: src
        source: "#untar/example_out"
    outputs:
      - id: classfile
