#!/usr/bin/env cwl-runner

cwlVersion: cwl:draft-4.dev1

class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: images.sbgenomics.com/rabix/bwa
    dockerImageId: 9d3b9b0359cf

  ResourceRequirement:
    coresMin: 4

inputs:
  reference:
    type: File
    inputBinding: { position: 2 }

  reads:
    type:
      type: array
      items: File
    inputBinding: { position: 3 }

  minimum_seed_length:
    type: int
    inputBinding: { position: 1, prefix: -m }

  min_std_max_min:
    type: { type: array, items: int }
    inputBinding:
      position: 1
      prefix: -I
      itemSeparator: ","

outputs:
  sam:
    type: File
    outputBinding: { glob: output.sam }

baseCommand: [bwa, mem]

arguments:
  - valueFrom: $(runtime.cores)
    position: 1
    prefix: -t

stdout: output.sam
