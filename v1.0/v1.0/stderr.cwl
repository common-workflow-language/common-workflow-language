#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: "Test of capturing stderr output in a docker container."
inputs: []
outputs:
  output_file:
    type: File
    outputBinding: {glob: error.txt}
baseCommand: [sh, -c, "echo foo 1>&2"]
stderr: error.txt
