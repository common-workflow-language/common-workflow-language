- id: "#index"
  class: CommandLineTool
  baseCommand: python
  arguments:
    - valueFrom: input.txt
      position: 1
  requirements:
    - class: CreateFileRequirement
      fileDef:
        - filename: input.txt
          fileContent:
            engine: "cwl:JsonPointer"
            script: job/index_file
  inputs:
    - id: "#index_file"
      type: File
    - id: "#index.py"
      type: File
      default:
        class: File
        path: index.py
      inputBinding:
        position: 0
  outputs:
    - id: "#index_result"
      type: File
      outputBinding:
        glob: input.txt
        secondaryFiles:
          - ".idx"

- id: "#search"
  class: CommandLineTool
  baseCommand: python
  inputs:
    - id: "#search_file"
      type: File
      inputBinding:
        position: 1
        secondaryFiles:
          - ".idx"
    - id: "#search.py"
      type: File
      default:
        class: File
        path: search.py
      inputBinding:
        position: 0
    - id: "#search_term"
      type: string
      inputBinding:
        position: 2
  outputs:
    - id: "#search_result"
      type: File
      outputBinding:
        glob: result.txt
  stdout: result.txt

- id: "#main"
  class: Workflow
  inputs:
    - id: "#infile"
      type: File
    - id: "#term"
      type: string
  outputs:
    - id: "#outfile"
      type: File
      source: "#search.search_result"

  steps:
    - run: {import: "#index"}
      inputs:
        - { id: "#index.index_file", source: "#infile" }
      outputs:
        - id: "#index.index_result"

    - run: {import: "#search"}
      inputs:
        - { id: "#search.search_file", source: "#index.index_result" }
        - { id: "#search.search_term", source: "#term" }
      outputs:
        - id: "#search.search_result"