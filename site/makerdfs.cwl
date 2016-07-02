cwlVersion: draft-4.dev3
class: CommandLineTool
inputs:
  schema:
    type: File
    inputBinding: {position: 1}
  target: string
outputs:
  out:
    type: File
    outputBinding:
      glob: $(inputs.target)
baseCommand: [python, "-mschema_salad", "--print-rdfs"]
stdout: $(inputs.target)
