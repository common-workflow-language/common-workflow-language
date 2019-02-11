#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8

inputs: []
baseCommand: "false"
outputs: []

successCodes: [ 1 ]
permanentFailCodes: [ 0 ]
temporaryFailCodes: [ 42 ]
