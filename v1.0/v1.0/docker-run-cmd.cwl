class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8
requirements:
  DockerRequirement:
    dockerPull: bash:4.4.12
  InlineJavascriptRequirement: {}
inputs: []
outputs:
  cow:
    type: File
    outputBinding:
      glob: cow
baseCommand: ["-c"]

arguments:
  - valueFrom: "${ return \"echo 'moo' > cow\" }"
