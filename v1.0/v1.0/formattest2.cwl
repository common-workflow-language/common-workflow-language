$namespaces:
  edam: http://edamontology.org/
$schemas:
  - EDAM.owl
class: CommandLineTool
cwlVersion: v1.0
doc: "Reverse each line using the `rev` command"
hints:
  ResourceRequirement:
    ramMin: 8
  DockerRequirement:
    dockerPull: "debian:stretch-slim"

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
    format: $(inputs.input.format)

baseCommand: rev
stdout: output.txt
