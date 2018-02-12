cwlVersion: v1.0
class: CommandLineTool
baseCommand: "true"

requirements:
  - class: InlineJavascriptRequirement
inputs:
  - id: parameter
    inputBinding:
      valueFrom: $(true)
      prefix: --a_prefix
    type: boolean?

outputs: []
