#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

class: CommandLineTool

inputs:
  - id: input
    type:
      type: array
      items: File

outputs:
  output_file:
    type: File
    outputBinding: {glob: output.txt}

arguments:
  - valueFrom: |
      ${
        var cmd = ["echo"];
        if (inputs.input.length == 0) {
           cmd.push('no_inputs');
        }
        else {
          for (var i = 0; i < inputs.input.length; i++) {
            var filesize = inputs.input[i].size;
            if (filesize == 0) {
              cmd.push("empty_file");
            } else if (filesize <= 16) {
              cmd.push("small_file");
            } else {
              cmd.push("big_file")
            }
          }
        }
        return cmd;
      }
baseCommand: []
stdout: output.txt
