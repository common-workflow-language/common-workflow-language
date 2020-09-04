class: Workflow
cwlVersion: v1.0
inputs: []
outputs: []
steps:
  step1:
    in:
      file1:
        default:
          class: File
          location: hello.txt
    out: [foo]
    run: test-cwl-out4.cwl
  step2:
    in:
      file1: step1/foo
      expect: {default: hello.txt}
    out: []
    run: checkname.cwl