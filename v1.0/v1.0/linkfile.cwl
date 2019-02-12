cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8

requirements:
  InitialWorkDirRequirement:
    listing:
      - $(inputs.src)

inputs:
  src:
    type: File
    inputBinding:
      position: 1
      valueFrom: $(self.nameroot).class

baseCommand: touch

outputs:
  classfile:
    type: File
    outputBinding:
      glob: "*.class"
