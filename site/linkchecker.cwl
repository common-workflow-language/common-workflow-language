class: CommandLineTool
cwlVersion: draft-4.dev3
requirements:
  - class: ShellCommandRequirement
  - class: InlineJavascriptRequirement
    expressionLib:
      - $include: cwlpath.js
hints:
  DockerRequirement:
    dockerFile: |
      FROM debian:8
      RUN apt-get update && \
          DEBIAN_FRONTEND=noninteractive apt-get -yq install w3c-linkchecker \
    dockerImageId: commonworkflowlanguage/checklink
  InitialWorkDirRequirement:
    listing: |
      ${
        var r = [];
        for (var i=0; i < inputs.dirs.length; i++) {
          if (inputs.dirs[i] != "") {
            r.push({
              "entryname": inputs.dirs[i],
              "entry": {
                "class": "Directory",
                "listing": [inputs.inp[i]]
              }
            });
          } else {
            r.push(inputs.inp[i]);
          }
        }
        return r;
      }

inputs:
  inp:
    type:
      type: array
      items: Directory
  target:
    type: string
outputs:
  out:
    type: File
    outputBinding:
      glob: $(inputs.target)

baseCommand: []
arguments:
  - "checklink"
  - "-X(http.*|mailto:.*)"
  - "-q"
  - valueFrom: |
      ${
        var r = [];
        for (var i=0; i < inputs.inp.length; i++) {
          if (inputs.dirs[i] != "") {
            r.push(inputs.dirs[i] + "/" + inputs.inp[i].basename);
          } else {
            r.push(inputs.inp[i].basename);
          }
        }
        return r;
      }
  - {valueFrom: " > ", shellQuote: false}
  - valueFrom: $(inputs.target)
  - {valueFrom: " && ! test -s", shellQuote: false}
  - valueFrom: $(inputs.target)