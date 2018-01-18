cwlVersion: v1.1.0-dev1
class: CommandLineTool
inputs:
  - id: "file1"
    type: File
    default:
      class: File
      path: default.txt
outputs: []
arguments: [cat,$(inputs.file1.path)]