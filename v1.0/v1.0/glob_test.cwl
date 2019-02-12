#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8

inputs: []
baseCommand: [touch, z, y, x, w, c, b, a]
outputs:
  letters:
    type: File[]
    outputBinding: { glob: '*' }
