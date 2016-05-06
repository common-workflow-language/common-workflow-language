#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: cwl:draft-4.dev1

inputs:
  reference:
    type: File
    inputBinding: { position: 2 }

  reads:
    type:
      type: array
      items: File
      inputBinding: { prefix: "-YYY" }
    inputBinding: { position: 3, prefix: "-XXX" }

outputs: []

baseCommand: [bwa, mem]
