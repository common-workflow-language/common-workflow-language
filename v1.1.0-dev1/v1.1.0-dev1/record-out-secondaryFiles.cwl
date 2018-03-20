class: CommandLineTool
cwlVersion: v1.1.0-dev1
inputs: []
outputs:
  record_output:
    type:
      type: record
      fields:
        f1:
          type: File
          secondaryFiles: .s2
          outputBinding:
            glob: A
        f2:
          type:
            type: array
            items: File
          secondaryFiles: .s3
          outputBinding:
            glob: [B, C]

baseCommand: touch
arguments: [A, A.s2, B, B.s3, C, C.s3]