class: CommandLineTool
cwlVersion: cwl:draft-3
baseCommand: ["cat", "example.conf"]

requirements:
  - class: CreateFileRequirement
    fileDef:
      - filename: example.conf
        fileContent: |
          CONFIGVAR=$(inputs.message)

inputs:
  - id: message
    type: string
outputs: []
