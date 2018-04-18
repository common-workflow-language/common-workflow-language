cwlVersion: v1.0
$graph:
- id: search
  class: CommandLineTool
  baseCommand: cat
  inputs:
    file:
      type: File
      inputBinding:
        position: 1
        valueFrom: $(self.path).idx
      default:
        class: File
        location: whale.txt
      secondaryFiles:
        - ".idx"
  outputs:
    result:
      type: File
      outputBinding:
        glob: result.txt
  stdout: result.txt

- id: main
  class: Workflow
  inputs: []
  outputs:
    outfile:
      type: File
      outputSource: search/result

  steps:
    search:
      run: "#search"
      in: []
      out: [result]
