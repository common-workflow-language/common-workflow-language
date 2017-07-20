class: Workflow
inputs:
  foo: string
outputs:
  bar: string
steps:
  step1:
    run: blub.cwl
    in: []
    out: [out]