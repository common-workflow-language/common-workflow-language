#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3.dev1"

class: CommandLineTool
requirements:
  - "@import": node-engine.cwl

hints:
  - class: DockerRequirement
    dockerPull: images.sbgenomics.com/rabix/bwa
    dockerImageId: 9d3b9b0359cf

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

outputs:
  - id: "#sam"
    type: "File"
    outputBinding: { "glob": "output.sam" }

baseCommand: ["bwa", "mem"]

arguments:
  - valueFrom:
      engine: "node-engine.cwl"
      script: "$job.allocatedResources.cpu"
    position: 1
    prefix: "-t"

stdout: "output.sam"
