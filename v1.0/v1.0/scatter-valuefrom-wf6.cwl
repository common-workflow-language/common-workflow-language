cwlVersion: v1.0
class: Workflow
requirements:
  - class: ScatterFeatureRequirement
  - class: StepInputExpressionRequirement
inputs:
  scattered_messages: string[]
outputs:
  out_message:
    type: File[]
    outputSource: step1/out_message
steps:
  step1:
    run: scatter-valueFrom-tool.cwl
    scatter: [scattered_message]
    scatterMethod: dotproduct
    in:
      scattered_message: scattered_messages
      message:
        valueFrom: "Hello"
    out: [out_message]
