class: CommandLineTool
inputs:
  - id: "#in"
    type: "string"
outputs:
  - id: "#out"
    type: "File"
requirements:
  - class: ExpressionEngineRequirement
    id: "node-engine.cwl"
environmentDefs:
  - env: "TEST_ENV"
    value:
      engine: node-engine.cwl
      script: "$job.in"
baseCommand: ["/bin/bash", "-c", "echo $TEST_ENV"]
stdout: {ref: "#out"}
