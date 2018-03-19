cwlVersion: v1.0
class: CommandLineTool
requirements:
  - class: InlineJavascriptRequirement
    expressionLib:
      - $include: cwlpath.js
inputs:
  source:
    type: File
    inputBinding: {position: 1}
  renderlist:
    type:
      - "null"
      - type: array
        items: string
        inputBinding: {prefix: "--only"}
    inputBinding: {position: 2}
  redirect:
    type:
      - "null"
      - type: array
        items: string
        inputBinding: {prefix: "--redirect"}
    inputBinding: {position: 2}
  brand:
    type: string
    inputBinding: {prefix: "--brand"}
  brandlink:
    type: string
    inputBinding: {prefix: "--brandlink"}
  target:
    type: string
  primtype:
    type: ["null", string]
    inputBinding: {prefix: "--primtype"}
  extra: File
outputs:
  out: stdout
  targetdir:
    type: string
    outputBinding:
      outputEval: |
        ${
          var m = inputs.target.match(/^([^/]+)\/[^/]/);
          if (m)
            return m[1];
          else
            return "";
        }
  extra_out:
    type: File
    outputBinding:
      outputEval: ${ return inputs.extra; }
baseCommand: [python, "-mschema_salad.makedoc"]
stdout: $(inputs.target)
