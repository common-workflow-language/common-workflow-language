cwlVersion: v1.0
class: CommandLineTool
requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 8

baseCommand: echo
inputs:
  file1:
    type: File?
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
