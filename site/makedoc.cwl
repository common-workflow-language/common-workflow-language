cwlVersion: "cwl:draft-3.dev4"
class: CommandLineTool
inputs:
  - id: source
    type: File
    inputBinding: {position: 1}
  - id: renderlist
    type:
      - "null"
      - type: array
        items: string
    inputBinding: {position: 2}
  - id: target
    type: string
outputs:
  - id: out
    type: File
    outputBinding:
      glob: $(inputs.target)
baseCommand: [python, "-mschema_salad.makedoc"]
stdout: $(inputs.target)
