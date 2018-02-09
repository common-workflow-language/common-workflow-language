cwlVersion: v1.0
class: CommandLineTool
baseCommand: "true"

requirements:
  - class: InlineJavascriptRequirement
inputs:
  - id: parameter
    inputBinding:
      valueFrom: $(true)
    type: boolean?

outputs: []
