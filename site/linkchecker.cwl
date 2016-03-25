class: CommandLineTool
requirements:
  - class: ShellCommandRequirement
  - class: InlineJavascriptRequirement
    expressionLib:
      - $include: cwlpath.js
hints:
  - class: DockerRequirement
    dockerFile: |
      FROM debian:8
      RUN apt-get update && \
          DEBIAN_FRONTEND=noninteractive apt-get -yq install w3c-linkchecker \
    dockerImageId: commonworkflowlanguage/checklink

inputs:
  - id: inp
    type:
      type: array
      items: File
  - id: dirs
    type:
      type: array
      items: string
  - id: target
    type: string
outputs:
  - id: out
    type: File
    outputBinding:
      glob: $(inputs.target)
baseCommand: []
arguments:
  - "mkdir"
  - "-p"
  - valueFrom: |
      ${
        var r = [];
        for (var i=0; i < inputs.dirs.length; i++) {
          if (inputs.dirs[i] != "") {
            r.push(inputs.dirs[i]);
          }
        }
        return r;
      }
  - {valueFrom: "&&", shellQuote: false}
  - valueFrom: |
      ${
        var r = [];
        for (var i=0; i < inputs.inp.length; i++) {
            if (i > 0) {
              r.push("&&");
            }
            r.push("ln");
            r.push("-s");
            r.push(inputs.inp[i].path);
            r.push(runtime.outdir + "/" + inputs.dirs[i]);
        }
        return r;
      }
  - {valueFrom: "&&", shellQuote: false}
  - "checklink"
  - "-X(http.*|mailto:.*)"
  - "-q"
  - valueFrom: |
      ${
        var r = [];
        for (var i=0; i < inputs.inp.length; i++) {
          r.push(cwl.path.basename(inputs.inp[i].path));
        }
        return r;
      }
  - {valueFrom: " > ", shellQuote: false}
  - valueFrom: $(inputs.target)
  - {valueFrom: " && ! test -s", shellQuote: false}
  - valueFrom: $(inputs.target)