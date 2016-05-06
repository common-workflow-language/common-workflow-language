cwlVersion: cwl:draft-4.dev1
$graph:
- id: echo
  class: CommandLineTool
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
    input_1:
      type: string

    input_2:
      type: string

  outputs:
    fileout:
      type: File
      source: "#collision/cat_step/fileout"

  steps:
    echo_1:
      run: "#echo"
      in:
        text: "#collision/input_1"
      out: [fileout]

    echo_2:
      run: "#echo"
      in:
        text: "#collision/input_2"
      out: [fileout]

    cat_step:
      run: "#cat"
      in:
        file1:
          source: "#collision/echo_1/fileout"
        file2:
          source: "#collision/echo_2/fileout"
      out: [fileout]
