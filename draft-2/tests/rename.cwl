class: CommandLineTool
baseCommand: "true"
requirements:
  - class: CreateFileRequirement
    fileDef:
      - filename:
          engine: "cwl:JsonPointer"
          script: job/newname
        fileContent:
          engine: "cwl:JsonPointer"
          script: job/srcfile
inputs:
  - id: "#srcfile"
    type: File
  - id: "#newname"
    type: string
outputs:
  - id: "#outfile"
    type: File
    outputBinding:
      glob:
        engine: "cwl:JsonPointer"
        script: job/newname
