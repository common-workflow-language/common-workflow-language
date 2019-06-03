#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
inputs: []
outputs:
  results:
    type: File
    outputBinding: { glob: results }
  # log:
  #   type: File
  #   outputBinding: { glob: log }
requirements:
  ShellCommandRequirement: {}
hints:
  ResourceRequirement:
    ramMin: 8
  DockerRequirement:
    dockerPull: debian:stretch-slim
arguments:
  - shellQuote: false
    valueFrom: |
      echo HOME=$HOME TMPDIR=$TMPDIR # > log
      if [ "$HOME" = "$(runtime.outdir)" ] && [ "$TMPDIR" = "$(runtime.tmpdir)" ]
      then
          echo success > results
      else
          echo failure > results
      fi
