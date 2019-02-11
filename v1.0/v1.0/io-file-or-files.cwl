#!/usr/bin/env cwl-runner

cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8

requirements:
  - class: InlineJavascriptRequirement

class: CommandLineTool

inputs:
  - id: input
    type:
      - "null"
      - File
      - type: array
        items: File

outputs:
  output_file:
    type: File
    outputBinding: {glob: output.txt}

arguments:
  - valueFrom: |
      ${
        var cmd = [];
        if (inputs.input === null) {
           cmd.push('echo');
           cmd.push('no_inputs');
        } else {
          cmd.push('cat');
          if (Array.isArray(inputs.input)) {
              for (var i = 0; i < inputs.input.length; i++) {
                 cmd.push(inputs.input[i].path);
              }
          } else {
            cmd.push(inputs.input.path);
          }
        }
        return cmd;
      }
baseCommand: []
stdout: output.txt
