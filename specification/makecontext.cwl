cwlVersion: "cwl:draft-3.dev1"
"@graph":
- id: makecontext
  class: CommandLineTool
  inputs:
    - id: schema
      type: File
      inputBinding: {}
    - id: target
      type: string
  outputs:
    - id: out
      type: File
      outputBinding:
        glob:
          engine: "cwl:JsonPointer"
          script: "job/target"
  baseCommand: [python, "-mschema_salad", "--print-jsonld-context"]
  stdout:
    engine: "cwl:JsonPointer"
    script: "job/target"

- id: makerdfs
  class: CommandLineTool
  inputs:
    - id: schema
      type: File
      inputBinding: {}
    - id: target
      type: string
  outputs:
    - id: out
      type: File
      outputBinding:
        glob:
          engine: "cwl:JsonPointer"
          script: "job/target"
  baseCommand: [python, "-mschema_salad", "--print-rdfs"]
  stdout:
    engine: "cwl:JsonPointer"
    script: "job/target"
