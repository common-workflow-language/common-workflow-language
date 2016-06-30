#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: cwl:draft-4.dev3
description: "Test of capturing stderr output in a docker container."
hints:
  DockerRequirement:
    dockerPull: debian:wheezy

inputs: []

outputs:
  output_file:
    type: stderr

baseCommand: egrep
successCodes: [2]

stderr: std.err
