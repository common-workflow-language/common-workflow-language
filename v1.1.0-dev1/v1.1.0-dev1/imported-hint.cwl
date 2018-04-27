#!/usr/bin/env cwl-runner
cwlVersion: v1.1.0-dev1
class: CommandLineTool
inputs: []
outputs:
  out: stdout

hints:
- $import: envvar.yml

baseCommand: ["/bin/sh", "-c", "echo $TEST_ENV"]

stdout: out
