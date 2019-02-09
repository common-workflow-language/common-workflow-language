cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 128
requirements:
  InlineJavascriptRequirement: {}
inputs:
  file1: File?
outputs:
  out:
    type: string
    outputBinding:
      glob: out.txt
      loadContents: true
      outputEval: $(self[0].contents)
stdout: out.txt
arguments: [echo, '$(inputs.file1 === null ? "t" : "f")']
