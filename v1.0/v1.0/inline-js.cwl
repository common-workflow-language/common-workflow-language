cwlVersion: v1.0
class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerPull: python:2-slim

inputs:
  - id: args.py
    type: File
    default:
      class: File
      location: args.py
    inputBinding:
      position: -1

outputs:
  - id: args
    type:
      type: array
      items: string

baseCommand: python

arguments:
  - prefix: -A
    valueFrom: $(1+1)
  - prefix: -B
    valueFrom: $("/foo/bar/baz".split('/').slice(-1)[0])
  - prefix: -C
    valueFrom: |
      ${
        var r = [];
        for (var i = 10; i >= 1; i--) {
          r.push(i);
        }
        return r;
      }
  # Test errors similar to https://github.com/common-workflow-language/cwltool/issues/648 are fixed
  - prefix: -D
    valueFrom: $(true)
  - prefix: -E
    valueFrom: $(false)
