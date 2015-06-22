class: CommandLineTool
inputs:
  - { id: "#in", type: "string" }
outputs:
  - id: "#out"
    type: "File"
    outputBinding:
      glob: "out"

requirements:
  - class: EnvVarRequirement
    envDef:
      - envName: "TEST_ENV"
        envValue:
          engine: "cwl:JsonPointer"
          script: "/job/in"

baseCommand: ["/bin/bash", "-c", "echo $TEST_ENV"]

stdout: "out"
