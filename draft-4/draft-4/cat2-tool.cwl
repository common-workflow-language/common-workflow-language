#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: cwl:draft-4.dev1
description: "Print the contents of a file to stdout using 'cat' running in a docker container."
hints:
  DockerRequirement:
    dockerPull: debian:wheezy
inputs:
  file1:
    type: File
outputs: []
baseCommand: cat
stdin: $(inputs.file1.path)
