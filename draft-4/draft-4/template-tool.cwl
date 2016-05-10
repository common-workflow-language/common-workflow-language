#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-4.dev1
class: CommandLineTool
requirements:
  - class: DockerRequirement
    dockerPull: "debian:8"
  - class: InlineJavascriptRequirement
    expressionLib:
      - { $include: underscore.js }
      - "var t = function(s) { return _.template(s)({'inputs': inputs}); };"
  - class: CreateFileRequirement
    fileDef:
      - filename: foo.txt
        fileContent: $(t("The file is <%= inputs.file1.path %>\n"))
inputs:
  - id: file1
    type: File
outputs: []
baseCommand: [cat, foo.txt]
