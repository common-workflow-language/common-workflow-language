class: CommandLineTool
inputs:
  - id: "#in"
    type: "string"
outputs:
  - id: "#out"
    type: "File"
    outputBinding:
      glob: "out"
requirements:
  - class: ExpressionEngineRequirement
    id: "node-engine.cwl"
  - class: EnvVarRequirement
    envDef:
      - envName: "TEST_ENV"
        envValue:
          class: Expression
          engine: node-engine.cwl
          script: "$job.in"
baseCommand: ["/bin/bash", "-c", "echo $TEST_ENV"]
stdout: "out"
