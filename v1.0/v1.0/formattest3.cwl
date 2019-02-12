$namespaces:
  edam: http://edamontology.org/
  gx: http://galaxyproject.org/formats/
$schemas:
  - EDAM.owl
  - gx_edam.ttl
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
    format: gx:fasta

outputs:
  output:
    type: File
    outputBinding:
      glob: output.txt
    format: $(inputs.input.format)

baseCommand: rev
stdout: output.txt
