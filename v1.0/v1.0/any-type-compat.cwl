cwlVersion: v1.0
class: Workflow

steps: []
inputs:
  input1:
    type: Any
  input2:
    type: Any[]
  input3:
    type: Any

outputs:
  - id: output1
    type: string[]
    outputSource: input1
  - id: output2
    type: string[]
    outputSource: input2
  - id: output3
    type: string
    outputSource: input3