$namespaces:
  edam: http://edamontology.org/
$schemas:
  - EDAM.owl
class: CommandLineTool
cwlVersion: cwl:draft-3
description: "Reverse each line using the `rev` command"

inputs:
  - id: input
    type: File
    inputBinding: {}
    format: edam:format_2330

outputs:
  - id: output
    type: File
    outputBinding:
      glob: output.txt
    format: $(inputs.input.format)

baseCommand: rev
stdout: output.txt
