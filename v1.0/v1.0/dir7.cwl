class: ExpressionTool
cwlVersion: v1.0
requirements:
  InlineJavascriptRequirement: {}
inputs:
  files: File[]
outputs:
  dir: Directory
expression: |
  ${
  return {"dir": {"class": "Directory", "basename": "a_directory", "listing": inputs.files}};
  }