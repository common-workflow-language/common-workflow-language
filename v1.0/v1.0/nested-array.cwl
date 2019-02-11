cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  letters:
    type:
      type: array
      items:
        type: array
        items: string
    inputBinding:
      position: 1
stdout: echo.txt
outputs:
  echo: stdout
