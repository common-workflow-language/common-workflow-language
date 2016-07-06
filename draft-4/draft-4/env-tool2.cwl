class: CommandLineTool
cwlVersion: cwl:v1.0.dev4
inputs:
  in: string
outputs:
  out:
    type: File
    outputBinding:
      glob: out

hints:
  EnvVarRequirement:
    envDef:
      TEST_ENV: $(inputs.in)

baseCommand: ["/bin/bash", "-c", "echo $TEST_ENV"]

stdout: out
