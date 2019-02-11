$namespaces:
  edam: "http://edamontology.org/"
cwlVersion: v1.0
class: CommandLineTool
doc: "Reverse each line using the `rev` command"
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  input:
    type: File
    inputBinding: {}
    format: edam:format_2330

outputs:
  output:
    type: File
    outputBinding:
      glob: output.txt
    format: edam:format_2330

baseCommand: rev
stdout: output.txt
