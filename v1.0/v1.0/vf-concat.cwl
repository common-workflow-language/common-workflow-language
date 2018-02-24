cwlVersion: v1.0
class: CommandLineTool
requirements:
  - class: InlineJavascriptRequirement

baseCommand: echo
inputs:
  - id: parameter
    type: string?
    inputBinding:
      valueFrom: $("a ")$("string")
outputs:
  out:
    type: string
    outputBinding:
      glob: output.txt
      loadContents: true
      outputEval: $(self[0].contents)
stdout: output.txt
