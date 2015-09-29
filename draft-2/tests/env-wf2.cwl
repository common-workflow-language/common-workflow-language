#!/usr/bin/env cwl-runner
class: Workflow

inputs:
    - { id: "#in", type: string }

outputs:
    - id: "#out"
      type: File
      source: "#step1.out"

requirements:
  - class: SubworkflowFeatureRequirement
  - class: EnvVarRequirement
    envDef:
      - envName: "TEST_ENV"
        envValue: "override"

steps:
  - id: "#step1"
    run: {import: env-tool2.cwl}
    inputs:
      - { id: "#step1.in", source: "#in"}
    outputs:
      - { id: "#step1.out" }
