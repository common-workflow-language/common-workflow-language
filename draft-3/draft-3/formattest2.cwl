"@context":
  "edam": "http://edamontology.org/"
class: CommandLineTool
cwlVersion: cwl:draft-3.dev1
description: "Reverse each line using the `rev` command"
requirements:
  - class: FormatOntologyRequirement
    formatOntologies:
      - EDAM.owl

inputs:
  - id: "#input"
    type: File
    inputBinding: {}
    format: edam:format_2330

outputs:
  - id: "#output"
    type: File
    outputBinding:
      glob: output.txt
    format:
      engine: cwl:JsonPointer
      script: /job/input/format


baseCommand: rev
stdout: output.txt
