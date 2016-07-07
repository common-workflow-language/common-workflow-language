#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: "Test of capturing stderr output in a docker container."
hints:
  DockerRequirement:
    dockerPull: debian:wheezy
inputs: []
outputs:
  output_file:
    type: File
    outputBinding: {glob: error.txt}
baseCommand: egrep
successCodes: [2]
stderr: error.txt
