cwlVersion: v1.0
class: Workflow
inputs:
  inp: File
  ex: string

outputs:
  classout:
    type: File
    outputSource: "#compile/classfile"

steps:
  untar:
    run: tar-param.cwl
    inputs:
      tarfile: inp
      extractfile: ex
    outputs: [example_out]

  compile:
    run: arguments.cwl
    inputs:
      src: untar/example_out
    outputs: [classfile]
