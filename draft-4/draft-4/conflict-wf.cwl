cwlVersion: cwl:draft-3
$graph:
- class: CommandLineTool
  id: echo
  inputs:
    - id: text
      type: string
      inputBinding: {}

  outputs:
    - id: fileout
      type: File
      outputBinding:
        glob: out.txt

  baseCommand: echo
  stdout: out.txt

- class: CommandLineTool
  id: cat
  inputs:
    - id: file1
      type: File
      inputBinding:
        position: 1
    - id: file2
      type: File
      inputBinding:
        position: 2

  outputs:
    - id: fileout
      type: File
      outputBinding:
        glob: out.txt

  baseCommand: cat
  stdout: out.txt

- class: Workflow
  id: collision

  inputs:
    - id: input_1
      type: string

    - id: input_2
      type: string

  outputs:
    - id: fileout
      type: File
      source: "#collision/cat_step/fileout"

  steps:
    - id: echo_1
      run: "#echo"
      inputs:
        - id: text
          source: "#collision/input_1"
      outputs:
        - id: fileout

    - id: echo_2
      run: "#echo"
      inputs:
        - id: text
          source: "#collision/input_2"
      outputs:
        - id: fileout

    - id: cat_step
      run: "#cat"
      inputs:
        - id: file1
          source: "#collision/echo_1/fileout"
        - id: file2
          source: "#collision/echo_2/fileout"
      outputs:
        - id: fileout