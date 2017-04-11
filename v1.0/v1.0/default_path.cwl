cwlVersion: v1.0
class: CommandLineTool
inputs:
  - id: "file1"
    type: File
    default:
      class: File
      path: default.txt
outputs: []
arguments: [cat,$(inputs.file1.path)]