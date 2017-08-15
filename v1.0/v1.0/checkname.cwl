cwlVersion: v1.0
class: CommandLineTool
inputs:
  file1: File
  expect: string
outputs: []
arguments: [test, '$(inputs.file1.path)', '=', '$(inputs.file1.dirname)/$(inputs.expect)']
