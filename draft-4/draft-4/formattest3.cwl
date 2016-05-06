$namespaces:
  edam: http://edamontology.org/
  gx: http://galaxyproject.org/formats/
$schemas:
  - EDAM.owl
  - gx_edam.ttl
class: CommandLineTool
cwlVersion: cwl:draft-4.dev1
description: "Reverse each line using the `rev` command"

inputs:
  - id: input
    type: File
    inputBinding: {}
    format: gx:fasta

outputs:
  - id: output
    type: File
    outputBinding:
      glob: output.txt
    format: $(inputs.input.format)

baseCommand: rev
stdout: output.txt
