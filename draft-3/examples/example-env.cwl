cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: env
requirements:
  - class: EnvVarRequirement
    envDef:
      - envName: HELLO
        envValue: $(inputs.message)
inputs:
  - id: message
    type: string
outputs: []
