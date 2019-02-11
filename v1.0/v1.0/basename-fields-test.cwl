cwlVersion: v1.0
class: Workflow

requirements:
  - class: StepInputExpressionRequirement

hints:
  ResourceRequirement:
    ramMin: 8

inputs:
  tool: File

outputs:
  rootFile:
    type: File
    outputSource: root/out
  extFile:
    type: File
    outputSource: ext/out

steps:
  root:
    run: echo-file-tool.cwl
    in:
      tool: tool
      in:
        valueFrom: $(inputs.tool.nameroot)
    out: [out]
  ext:
    run: echo-file-tool.cwl
    in:
      tool: tool
      in:
        valueFrom: $(inputs.tool.nameext)
    out: [out]

