class: Workflow
cwlVersion: v1.0
inputs:
  inp1:
    type: string
    default: hello inp1
  inp2:
    type: string
    default: hello inp2
outputs:
  out:
    type: string
    outputSource: step1/out
steps:
  step1:
    in:
      in: inp1
      in2: inp2
    out: [out]
    run: fail-unspecified-input.cwl
