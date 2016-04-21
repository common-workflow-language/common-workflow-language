#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: cwl:draft-3

inputs:
    - { id: in, type: string }

outputs:
    - id: out
      type: File
      source: "#step1/out"

requirements:
  - class: SubworkflowFeatureRequirement
  - class: EnvVarRequirement
    envDef:
      - envName: TEST_ENV
        envValue: override

steps:
  - id: step1
    run: env-tool2.cwl
    inputs:
      - { id: in, source: "#in" }
    outputs:
      - { id: out }
