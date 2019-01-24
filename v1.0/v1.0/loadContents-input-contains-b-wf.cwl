cwlVersion: v1.0
class: Workflow

requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  in:
    type: File

outputs:
  contains_b:
    type: boolean
    outputSource: check_file/contains_b

steps:

  create_file:
    run:
      class: CommandLineTool
      inputs:
        file1:
          type: File
          inputBinding: {position: 1}
      outputs:
        output:
          type: File
          outputBinding: {glob: out.txt}

      baseCommand: cat
      stdout: out.txt

    in: {file1: in}
    out: [ output ]

  check_file:
    run:
      class: ExpressionTool
      requirements: { InlineJavascriptRequirement: {} }
      inputs:
      - { id: bytes, type: File, inputBinding: { loadContents: true } }
      outputs: { contains_b: boolean }
      expression: |
        ${
           return {"contains_b": inputs.bytes.contents.indexOf("b") >= 0};
        }
    in:
      bytes:
        source: create_file/output

    out: [ contains_b ]
