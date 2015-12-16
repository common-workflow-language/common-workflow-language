cwlVersion: "cwl:draft-3.dev3"
"@graph":
- id: makecontext
  class: CommandLineTool
  inputs:
    - id: schema
      type: File
      inputBinding: {position: 1}
    - id: target
      type: string
  outputs:
    - id: out
      type: File
      outputBinding:
        glob: $(inputs.target)
  baseCommand: [python, "-mschema_salad", "--print-jsonld-context"]
  stdout: $(inputs.target)

- id: makerdfs
  class: CommandLineTool
  inputs:
    - id: schema
      type: File
      inputBinding: {position: 1}
    - id: target
      type: string
  outputs:
    - id: out
      type: File
      outputBinding:
        glob: $(inputs.target)
  baseCommand: [python, "-mschema_salad", "--print-rdfs"]
  stdout: $(inputs.target)
