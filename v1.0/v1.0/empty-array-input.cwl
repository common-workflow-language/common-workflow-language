#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

hints:
  - class: ResourceRequirement
    ramMin: 8
  - class: DockerRequirement
    dockerPull: python:2-slim

inputs:
  - id: array
    type: { type: array, items: int }
    inputBinding:
      position: 1
      prefix: -I
      itemSeparator: ","

  - id: args.py
    type: File
    default:
      class: File
      location: args.py
    inputBinding:
      position: -1

outputs:
  - id: args
    type:
      type: array
      items: string

baseCommand: python
