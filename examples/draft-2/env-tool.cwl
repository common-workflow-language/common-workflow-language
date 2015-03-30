class: CommandLineTool
inputs:
  - id: "#in"
    type: "string"
outputs:
  - id: "#out"
    type: "File"
environmentDefs:
  - env: "TEST_ENV"
    value:
      class: JavascriptExpression
      script: "$job.in"
baseCommand: ["/bin/bash", "-c", "echo $TEST_ENV"]
stdout: {ref: "#out"}
