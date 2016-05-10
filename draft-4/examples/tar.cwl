cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: [tar, xf]
inputs:
  - id: tarfile
    type: File
    inputBinding:
      position: 1
outputs:
  - id: example_out
    type: File
    outputBinding:
      glob: hello.txt
