cwlVersion: cwl:draft-3
class: CommandLineTool
hints:
  - class: DockerRequirement
    dockerPull: java:7
baseCommand: javac

requirements:
  - class: InlineJavascriptRequirement
  - class: CreateFileRequirement
    fileDef:
      - filename: $(inputs.src.path.split('/').slice(-1)[0])
        fileContent: $(inputs.src)

inputs:
  - id: src
    type: File
    inputBinding:
      position: 1
      valueFrom: $(inputs.src.path.split('/').slice(-1)[0])

outputs:
  - id: classfile
    type: File
    outputBinding:
      glob: "*.class"
