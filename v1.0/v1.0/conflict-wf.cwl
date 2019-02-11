cwlVersion: v1.0
$graph:
- id: echo
  class: CommandLineTool
  hints:
    ResourceRequirement:
      ramMin: 8
  inputs:
    text:
      type: string
      inputBinding: {}

  outputs:
    fileout:
      type: File
      outputBinding:
        glob: out.txt

  baseCommand: echo
  stdout: out.txt

- id: cat
  class: CommandLineTool
  hints:
    ResourceRequirement:
      ramMin: 8

  inputs:
    file1:
      type: File
      inputBinding:
        position: 1
    file2:
      type: File
      inputBinding:
        position: 2

  outputs:
    fileout:
      type: File
      outputBinding:
        glob: out.txt

  baseCommand: cat
  stdout: out.txt

- class: Workflow
  id: collision

  inputs:
    input_1: string
    input_2: string

  outputs:
    fileout:
      type: File
      outputSource: cat_step/fileout

  steps:
    echo_1:
      run: "#echo"
      in:
        text: input_1
      out: [fileout]

    echo_2:
      run: "#echo"
      in:
        text: input_2
      out: [fileout]

    cat_step:
      run: "#cat"
      in:
        file1:
          source: echo_1/fileout
        file2:
          source: echo_2/fileout
      out: [fileout]
