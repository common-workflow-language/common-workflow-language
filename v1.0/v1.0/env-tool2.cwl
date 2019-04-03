class: CommandLineTool
cwlVersion: v1.0
inputs:
  in: string
outputs:
  out:
    type: File
    outputBinding:
      glob: out

hints:
  ResourceRequirement:
    ramMin: 8
  EnvVarRequirement:
    envDef:
      TEST_ENV: $(inputs.in)

baseCommand: ["echo", "$TEST_ENV"]

stdout: out
