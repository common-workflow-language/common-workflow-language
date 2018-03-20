class: Workflow
cwlVersion: v1.1.0-dev1
inputs:
  record_input:
    type:
      type: record
      fields:
        f1:
          type: File
        f2:
          type:
            type: array
            items: File
outputs: []
steps:
  step1:
    in:
      record_input: record_input
    out: []
    run: record-in-secondaryFiles.cwl