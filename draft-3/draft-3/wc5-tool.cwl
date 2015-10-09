#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: "cwl:draft-3.dev1"

inputs:
    - { id: "#file1", type: {type: array, items: File}, inputBinding: {} }
outputs:
    - id: "#output"
      type: int
      outputBinding:
        glob: output.txt
        loadContents: true
        outputEval:
            engine: cwl:JavascriptEngine
            script: |
              {
                var s = $self[0].contents.split(/\r?\n/);
                return parseInt(s[s.length-2]);
              }
stdout: output.txt
baseCommand: wc
