#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: cwl:draft-3

inputs:
  - id: reference
    type: File
    inputBinding: { position: 2 }

  - id: reads
    type:
      type: array
      items: File
      inputBinding: { prefix: "-YYY" }
    inputBinding: { position: 3, prefix: "-XXX" }

outputs: []

baseCommand: [bwa, mem]
