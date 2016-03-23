class: CommandLineTool
baseCommand: [tar, xvf]
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
