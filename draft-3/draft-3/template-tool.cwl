#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
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
        fileContent: >
          $(t("The file is <%= inputs.file1.path.split('/').slice(-1)[0] %>\n"))
inputs:
  - id: file1
    type: File
outputs:
  - id: foo
    type: File
    outputBinding:
      glob: foo.txt
baseCommand: [cat, foo.txt]
