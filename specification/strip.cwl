class: CommandLineTool
inputs:
  - id: "#strip_leading_lines_in"
    type: File
    inputBinding: {}
  - id: "#strip_leading_lines_count"
    type: int
    inputBinding:
      prefix: "-n+"
      separate: false
outputs:
  - id: "#strip_leading_lines_out"
    type: File
    outputBinding:
      glob: "_tail_tmp.txt"
baseCommand: "tail"
stdout: "_tail_tmp.txt"
