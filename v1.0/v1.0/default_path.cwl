cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  - id: "file1"
    type: File
    default:
      class: File
      path: whale.txt
outputs: []
arguments: [cat,$(inputs.file1.path)]
