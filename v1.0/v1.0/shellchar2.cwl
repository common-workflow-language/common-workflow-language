#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: |
  Ensure that `shellQuote: true` is the default behavior when
  ShellCommandRequirement is in effect.
requirements:
  ShellCommandRequirement: {}
inputs: []
outputs:
  stdout_file: stdout
  stderr_file: stderr
baseCommand: echo
arguments: ["foo 1>&2"]
