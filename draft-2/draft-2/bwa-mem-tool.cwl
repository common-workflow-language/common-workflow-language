#!/usr/bin/env cwl-runner

class: CommandLineTool
requirements:
  - import: node-engine.cwl

inputs:
  - id: "#reference"
    type: File
    inputBinding: { position: 2 }

  - id: "#reads"
    type:
      type: array
      items: File
    inputBinding: { position: 3 }

  - id: "#minimum_seed_length"
    type: int
    inputBinding: { position: 1, prefix: "-m" }

  - id: "#min_std_max_min"
    type: { type: array, items: int }
    inputBinding:
      position: 1
      prefix: "-I"
      itemSeparator: ","

  - id: "#args.py"
    type: File
    default:
      class: File
      path: args.py
    inputBinding:
      position: -1

outputs:
  - id: "#sam"
    type: ["null", "File"]
    outputBinding: { "glob": "output.sam" }
  - id: "#args"
    type:
      type: array
      items: string

baseCommand: python

arguments:
  - "bwa"
  - "mem"
  - valueFrom:
      engine: "node-engine.cwl"
      script: "$job.allocatedResources.cpu"
    position: 1
    prefix: "-t"

stdout: "output.sam"
