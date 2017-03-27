cwlVersion: v1.0
class: Workflow
inputs:
  example_flag:
    type: boolean
    inputBinding:
      position: 1
      prefix: -f

outputs: []

steps:
  example_flag:
    in: []
    out: []
    run:
      id: blah
      class: CommandLineTool
      inputs: []
      outputs: []