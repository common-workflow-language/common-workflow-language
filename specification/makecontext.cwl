- id: "#makecontext"
  class: CommandLineTool
  inputs:
    - id: "#makecontext_target"
      type: string
  outputs:
    - id: "#makecontext_out"
      type: File
      outputBinding:
        glob:
          engine: "cwl:JsonPointer"
          script: "job/makecontext_target"
  baseCommand: [python, "-mcwltool", "--print-jsonld-context"]
  stdout:
    engine: "cwl:JsonPointer"
    script: "job/makecontext_target"

- id: "#makerdfs"
  class: CommandLineTool
  inputs:
    - id: "#makerdfs_target"
      type: string
  outputs:
    - id: "#makerdfs_out"
      type: File
      outputBinding:
        glob:
          engine: "cwl:JsonPointer"
          script: "job/makerdfs_target"
  baseCommand: [python, "-mcwltool", "--print-rdfs"]
  stdout:
    engine: "cwl:JsonPointer"
    script: "job/makerdfs_target"
