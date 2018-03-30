cwlVersion: v1.1.0-dev1
class: Workflow
requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
inputs:
  my_file:
    type: File
    loadContents: true

steps:
  one:
    run:
      class: ExpressionTool
      requirements: { InlineJavascriptRequirement: {} }
      inputs: { my_number: int }
      outputs: { my_int: int }
      expression: |
        ${ return { "my_int": inputs.my_number }; }
    in:
      my_number:
        source: my_file
        valueFrom: $(parseInt(self.contents))
    out: [ my_int ]

outputs:
  my_int:
    type: int
    outputSource: one/my_int