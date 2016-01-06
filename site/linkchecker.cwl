class: CommandLineTool
requirements:
  - class: ShellCommandRequirement
  - class: InlineJavascriptRequirement
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
  - "linkchecker"
  - "-a"
  - "--ignore-url=http.*"
  - "--ignore-url=mailto:.*"
  - valueFrom: |
      ${
        var r = [];
        for (var i=0; i < inputs.inp.length; i++) {
          r.push(inputs.inp[i].path.split('/').slice(-1)[0]);
        }
        return r;
      }
stdout: $(inputs.target)
