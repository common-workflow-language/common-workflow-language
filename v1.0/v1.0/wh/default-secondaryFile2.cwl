cwlVersion: v1.0
$graph:

- id: main
  class: Workflow
  inputs: []
  outputs:
    outfile:
      type: File
      outputSource: search/result

  steps:
    search:
      run: search.cwl
      in: []
      out: [result]
