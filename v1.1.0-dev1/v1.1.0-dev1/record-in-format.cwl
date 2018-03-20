class: CommandLineTool
cwlVersion: v1.1.0-dev1
inputs:
  regular_input:
    type: File
    format: http://example.com/format1
  record_input:
    type:
      type: record
      fields:
        f1:
          type: File
          format: http://example.com/format1
        f2:
          type:
            type: array
            items: File
          format: http://example.com/format2
outputs: []
arguments: ['true']