#!/usr/bin/env cwl-runner
cwlVersion: v1.1.0-dev1
class: Workflow

inputs: []
outputs:
  outfile:
    type: File
    outputSource: second/outfile

steps:
  first:
    run:
      class: CommandLineTool
      baseCommand: [ mkdir, directory ]
      inputs: []
      outputs:
        dir:
          type: Directory
          outputBinding: { glob: directory }
    in: {}
    out: [ dir ]

  second:
    run:
      class: CommandLineTool
      baseCommand: [ touch, directory/file ]
      requirements:
        InitialWorkDirRequirement:
          listing:
            - entry: $(inputs.dir)
      inputs:
        dir: Directory
      outputs:
        outfile:
          type: File
          outputBinding: { glob: directory/file }

    in: { dir: first/dir }
    out: [ outfile ]
