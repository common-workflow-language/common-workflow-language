class: CommandLineTool
inputs:
  - id: inp
    type: File
    inputBinding:
      position: 1
outputs: []
baseCommand: linkchecker
arguments: ["-a", "--ignore-url=http.*", "--ignore-url=mailto:.*"]
