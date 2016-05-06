#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-4.dev1
class: CommandLineTool
description: "Print the contents of a file to stdout using 'cat' running in a docker container."
hints:
  DockerRequirement:
    dockerPull: "debian:wheezy"
  BlibberBlubberFakeRequirement:
    fakeField: fraggleFroogle
inputs:
  file1:
    type: File
    label: "Input File"
    description: "The file that will be copied using 'cat'"
    inputBinding: {position: 1}
outputs:
  output_file:
    type: File
    outputBinding: {glob: output.txt}
baseCommand: cat
stdout: output.txt
