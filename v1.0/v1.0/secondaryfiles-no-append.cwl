cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  in:
    type: File
    inputBinding:
      position: 1
    secondaryFiles:
    - ^^
outputs:
  out:
    type: File
    outputBinding:
      outputEval: $(inputs.in)
