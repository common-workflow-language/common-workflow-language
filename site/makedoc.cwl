cwlVersion: "cwl:draft-3.dev4"
class: CommandLineTool
requirements:
  - class: InlineJavascriptRequirement
    expressionLib:
      - $include: cwlpath.js
inputs:
  - id: source
    type: File
    inputBinding: {position: 1}
  - id: renderlist
    type:
      - "null"
      - type: array
        items: string
        inputBinding: {prefix: "--only"}
    inputBinding: {position: 2}
  - id: redirect
    type:
      - "null"
      - type: array
        items: string
        inputBinding: {prefix: "--redirect"}
    inputBinding: {position: 2}
  - id: brand
    type: string
    inputBinding: {prefix: "--brand"}
  - id: brandlink
    type: string
    inputBinding: {prefix: "--brandlink"}
  - id: target
    type: string
  - id: primtype
    type: ["null", string]
    inputBinding: {prefix: "--primtype"}
outputs:
  - id: out
    type: File
    outputBinding:
      glob: $(inputs.target)
  - id: targetdir
    type: string
    outputBinding:
      outputEval: $(cwl.path.dirname(inputs.target))
baseCommand: [python, "-mschema_salad.makedoc"]
stdout: $(inputs.target)
