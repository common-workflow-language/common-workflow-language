cwlVersion: v1.0
class: Workflow

requirements:
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: InlineJavascriptRequirement

inputs:
  int_1:
    type:
      - int
      - string
  int_2:
    type:
      - int
      - string

outputs:
  result:
    type: File
    outputSource: sum/result

steps:
  sum:
    in:
      data:
        source: [int_1, int_2]
        valueFrom: |
          ${
            var sum = 0;
            for (var i = 0; i < self.length; i++){
              sum += self[i];
            };
            return sum;
          }
    out:
    - result
    run:
      class: CommandLineTool
      inputs:
        data:
          type: int
          inputBinding: {}
      baseCommand: echo
      stdout: result.txt
      outputs:
        result:
          type: stdout

