#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0
baseCommand: ["cat", "example.conf"]
hints:
  ResourceRequirement:
    ramMin: 8

requirements:
  InitialWorkDirRequirement:
    listing:
      - entryname: example.conf
        entry: |
          CONFIGVAR=$(inputs.message)

inputs:
  message: string
outputs:
  out:
    type: File
    outputBinding:
      glob: example.conf
