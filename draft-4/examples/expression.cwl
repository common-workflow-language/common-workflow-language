cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: echo

requirements:
  - class: InlineJavascriptRequirement

inputs: []
outputs: []
arguments:
  - valueFrom: $(1+1)
    prefix: -A
  - valueFrom: $("/foo/bar/baz".split('/').slice(-1)[0])
    prefix: -B
  - valueFrom: |
      ${
        var r = [];
        for (var i = 10; i >= 1; i--) {
          r.push(i);
        }
        return r;
      }
    prefix: -C