#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool

inputs: []
baseCommand: /bin/false
outputs: []

successCodes: [ 1 ]
permanentFailCodes: [ 0 ]
temporaryFailCodes: [ 42 ]
