class: CommandLineTool
requirements:
  - class: ShellCommandRequirement
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerFile: |
      FROM debian:8
      RUN apt-get update && \
          DEBIAN_FRONTEND=noninteractive apt-get -yq install w3c-checklink \
    dockerImageId: commonworkflowlanguage/checklink

inputs:
  - id: inp
    type:
      type: array
      items: File
  - id: target
    type: string
outputs:
  - id: out
    type: File
    outputBinding:
      glob: $(inputs.target)
baseCommand: []
arguments:
  - "ln"
  - "-s"
  - valueFrom: $(inputs.inp)
  - valueFrom: $(runtime.outdir)
  - {valueFrom: ";", shellQuote: false}
  - "checklink"
  - "-X(http.*|mailto:.*)"
  - "-q"
  - valueFrom: |
      ${
        var r = [];
        for (var i=0; i < inputs.inp.length; i++) {
          r.push(inputs.inp[i].path.split('/').slice(-1)[0]);
        }
        return r;
      }
  - {valueFrom: " > ", shellQuote: false}
  - valueFrom: $(inputs.target)
  - {valueFrom: " && ! test -s", shellQuote: false}
  - valueFrom: $(inputs.target)