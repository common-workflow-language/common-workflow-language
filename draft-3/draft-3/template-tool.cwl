#!/usr/bin/env cwl-runner
cwlVersion: "cwl:draft-3.dev2"
class: CommandLineTool
requirements:
  - class: DockerRequirement
    dockerPull: "debian:8"
  - class: InlineJavascriptRequirement
    expressionLib:
      - { "@include": underscore.js }
      - "var t = function(s) { return _.template(s)({'$job': $job}); };"
  - class: CreateFileRequirement
    fileDef:
      - filename: foo.txt
        fileContent: $(t("The file is <%= $job.file1.path %>\n"))
inputs:
  - id: file1
    type: File
outputs: []
baseCommand: [cat, foo.txt]
