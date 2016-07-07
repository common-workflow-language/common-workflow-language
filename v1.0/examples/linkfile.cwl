cwlVersion: v1.0
class: CommandLineTool
hints:
  DockerRequirement:
    dockerPull: java:7
baseCommand: javac

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirirement
    listing:
      - $(inputs.src)

inputs:
  src:
    type: File
    inputBinding:
      position: 1
      valueFrom: $(inputs.src.basename)

outputs:
  classfile:
    type: File
    outputBinding:
      glob: "*.class"
