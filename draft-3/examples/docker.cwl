cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: node
hints:
  - class: DockerRequirement
    dockerPull: node:slim
inputs:
  - id: src
    type: File
    inputBinding:
      position: 1
outputs: []
