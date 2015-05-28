#!/usr/bin/env cwl-runner

class: CommandLineTool

inputs:
  - { id: "#file1", type: File }

"outputs":
  - { id: "#output", type: File,  outputBinding: { glob: output } }

baseCommand: ["wc"]

stdin:
  engine: "cwl:JsonPointer"
  script: job/file1/path

stdout: output
