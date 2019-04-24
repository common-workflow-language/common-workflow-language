class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8
requirements:
  DockerRequirement:
    dockerPull: bash:4.4.12
inputs: []
outputs:
  cow:
    type: File
    outputBinding:
      glob: cow

arguments:
  - valueFrom: "-c"
    position: 0
  - valueFrom: "echo 'moo' > cow"
    position: 1
