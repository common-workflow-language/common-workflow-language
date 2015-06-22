#!/usr/bin/env cwl-runner
class: Workflow

inputs:
    - { id: "#in", type: string }

outputs:
    - id: "#out"
      type: File
      connect: {"source": "#step1_output"}

requirements:
  - class: SubworkflowFeatureRequirement
  - class: EnvVarRequirement
    envDef:
      - envName: "TEST_ENV"
        envValue: "override"

steps:
  - id: "#step1"
    run: {import: env-tool1.cwl}
    inputs:
      - { param: "env-tool1.cwl#in", connect: {source: "#in"} }
    outputs:
      - { id: "#step1_output", param: "env-tool1.cwl#out" }
