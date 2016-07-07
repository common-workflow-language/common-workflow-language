class: CommandLineTool
cwlVersion: v1.0
baseCommand: ["cat", "example.conf"]

requirements:
  InitialWorkDirRequirirement:
    listing:
      example.conf: |
        CONFIGVAR=$(inputs.message)

inputs:
  message: string
outputs: []
