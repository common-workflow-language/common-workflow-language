#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
doc: |
  Ensure that arguments containing shell directives are not interpreted and
  that `shellQuote: false` has no effect when ShellCommandRequirement is not in
  effect.
hints:
  ResourceRequirement:
    ramMin: 8
inputs: []
outputs:
  stdout_file: stdout
  stderr_file: stderr
baseCommand: echo
arguments: [{valueFrom: "foo 1>&2", shellQuote: false}]
