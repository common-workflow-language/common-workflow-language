#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-4.dev1

inputs:
    file1:
      type: File
      default: {class: File, path: hello.txt}
outputs:
    count_output:
      type: int
      source: "#step1/output"
steps:
  step1:
    run: wc2-tool.cwl
    in:
      file1:
        source: "#file1"
    out: [output]
