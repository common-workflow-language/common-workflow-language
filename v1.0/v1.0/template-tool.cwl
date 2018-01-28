#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
requirements:
  - class: InlineJavascriptRequirement
    expressionLib:
      - { $include: underscore.js }
      - "var t = function(s) { return _.template(s, {variable: 'data'})({'inputs': inputs}); };"
  - class: InitialWorkDirRequirement
    listing:
      - entryname: foo.txt
        entry: $(t("The file is <%= data.inputs.file1.path.split('/').slice(-1)[0] %>\n"))
hints:
  DockerRequirement:
    dockerPull: "debian:stretch-slim"
inputs:
  - id: file1
    type: File
outputs:
  - id: foo
    type: File
    outputBinding:
      glob: foo.txt
baseCommand: [cat, foo.txt]
