#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs:
  special_file:
    type: File
    default:
      class: File
      path: special_file

outputs:
  cores:
    type: File
    outputSource: report/output

steps:
  count:
    in:
      special_file: special_file
    out: [output]
    run: dynresreq.cwl

  report:
    in:
      file1: count/output
    out: [output]
    run: cat-tool.cwl
