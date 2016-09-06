#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.1.0-dev1
requirements:
  - class: InlineJavascriptRequirement

inputs:
    file1:
      type: File
      inputBinding: {}
outputs:
    - id: output
      type: int
      outputBinding:
        glob: output.txt
        loadContents: true
        outputEval: |
          ${
            var s = self[0].contents.split(/\r?\n/);
            return parseInt(s[s.length-2]);
          }
stdout: output.txt
baseCommand: wc
