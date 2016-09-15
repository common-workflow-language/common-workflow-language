#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

inputs:
    in: string

outputs:
    out:
      type: File
      outputSource: step1/out

steps:
  step1:
    run: env-tool2.cwl
    requirements:
      EnvVarRequirement:
        envDef:
          TEST_ENV: override
    in:
      in: in
    out: [out]
