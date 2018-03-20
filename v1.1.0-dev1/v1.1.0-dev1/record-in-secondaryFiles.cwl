class: CommandLineTool
cwlVersion: v1.1.0-dev1
inputs:
  record_input:
    type:
      type: record
      fields:
        f1:
          type: File
          secondaryFiles: .s2
        f2:
          type:
            type: array
            items: File
          secondaryFiles: .s3
outputs: []
baseCommand: test
arguments: [-f, $(inputs.record_input.f1.path).s2,
  '-a', '-f', '$(inputs.record_input.f2[0].path).s3',
  '-a', '-f', '$(inputs.record_input.f2[1].path).s3']