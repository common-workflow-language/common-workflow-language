cwlVersion: v1.0
$graph:
  - id: tool
    class: CommandLineTool
    requirements:
      InlineJavascriptRequirement:
        expressionLib:
          - "function foo() { return 2; }"
    inputs: []
    outputs:
      out: stdout
    arguments: [echo, $(foo())]
    stdout: whatever.txt

  - id: wf
    class: Workflow
    requirements:
      InlineJavascriptRequirement:
        expressionLib:
          - "function bar() { return 1; }"
    inputs: []
    outputs:
      out:
        type: File
        outputSource: tool/out
    steps:
      tool:
        run: "#tool"
        in: {}
        out: [out]