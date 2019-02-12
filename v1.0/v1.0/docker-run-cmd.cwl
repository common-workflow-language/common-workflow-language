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
baseCommand: ["-c", "echo 'moo' > cow"]
