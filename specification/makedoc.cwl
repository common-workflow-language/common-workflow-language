class: CommandLineTool
inputs:
  - id: "#makedoc_source"
    type: File
    inputBinding: {position: 1}
  - id: "#makedoc_title"
    type: ["null", string]
    inputBinding: {position: 2}
  - id: "#makedoc_target"
    type: string
outputs:
  - id: "#makedoc_out"
    type: File
    outputBinding:
      glob:
        engine: "cwl:JsonPointer"
        script: "job/makedoc_target"
baseCommand: [python, "-mcwltool.avro_ld.makedoc"]
stdout:
  engine: "cwl:JsonPointer"
  script: "job/makedoc_target"
