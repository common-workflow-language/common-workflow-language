#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: "Test of capturing stderr output in a docker container."
requirements:
  ShellCommandRequirement: {}
inputs: []
outputs:
  output_file:
    type: stderr
arguments:
 - { valueFrom: "echo foo 1>&2", shellQuote: False }
