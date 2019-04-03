class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  in: string
outputs:
  out:
    type: File
    outputBinding:
      glob: out

requirements:
  EnvVarRequirement:
    envDef:
      TEST_ENV: $(inputs.in)
  ShellCommandRequirement: {}

arguments:
  - valueFrom: "/bin/sh"
    position: 1
    shellQuote: false
  - valueFrom: "-c"
    position: 2
    shellQuote: false
  - valueFrom: "echo $TEST_ENV"
    position: 3
    shellQuote: true


stdout: out
