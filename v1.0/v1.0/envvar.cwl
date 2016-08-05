class: CommandLineTool
cwlVersion: v1.0
inputs: []
outputs: []
requirements:
  ShellCommandRequirement: {}
arguments: [
  echo, {valueFrom: '"HOME=$HOME"', shellQuote: false}, {valueFrom: '"TMPDIR=$TMPDIR"', shellQuote: false},
  {valueFrom: '&&', shellQuote: false},
  test, {valueFrom: '"$HOME"', shellQuote: false}, "=", $(runtime.outdir),
  "-a", {valueFrom: '"$TMPDIR"', shellQuote: false}, "=", $(runtime.tmpdir)]
