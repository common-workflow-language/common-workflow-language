class: CommandLineTool
cwlVersion: v1.1.0-dev1
inputs:
  record_input:
    type:
      type: record
      fields:
        f1: File
        f2: File[]
outputs:
  f1out:
    type: File
    format: http://example.com/format1
    outputBinding:
      outputEval: $(inputs.record_input.f1)
  record_output:
    type:
      type: record
      fields:
        f2out:
          type: File
          format: http://example.com/format2
          outputBinding:
            outputEval: $(inputs.record_input.f2[0])
arguments: ['true']