cwlVersion: cwl:draft-3
$graph:
- id: index
  class: CommandLineTool
  baseCommand: python
  arguments:
    - valueFrom: input.txt
      position: 1
  requirements:
    - class: CreateFileRequirement
      fileDef:
        - filename: input.txt
          fileContent: $(inputs.file)
    - class: InlineJavascriptRequirement

  inputs:
    - id: file
      type: File
    - id: index.py
      type: File
      default:
        class: File
        path: index.py
      inputBinding:
        position: 0
  outputs:
    - id: result
      type: File
      outputBinding:
        glob: input.txt
      secondaryFiles:
        - ".idx1"
        - "^.idx2"
        - '$(self.path+".idx3")'
        - '$({"path": self.path+".idx4", "class": "File"})'
        - '${ return self.path+".idx5"; }'

- id: search
  class: CommandLineTool
  baseCommand: python
  requirements:
    - class: InlineJavascriptRequirement
  inputs:
    - id: file
      type: File
      inputBinding:
        position: 1
      secondaryFiles:
        - ".idx1"
        - "^.idx2"
        - '$(self.path+".idx3")'
        - '$({"path": self.path+".idx4", "class": "File"})'
        - '${ return self.path+".idx5"; }'
    - id: search.py
      type: File
      default:
        class: File
        path: search.py
      inputBinding:
        position: 0
    - id: term
      type: string
      inputBinding:
        position: 2
  outputs:
    - id: result
      type: File
      outputBinding:
        glob: result.txt
  stdout: result.txt

- id: main
  class: Workflow
  inputs:
    - id: infile
      type: File
    - id: term
      type: string
  outputs:
    - id: outfile
      type: File
      source: "#main/search/result"
    - id: indexedfile
      type: File
      source: "#main/index/result"

  steps:
    - id: index
      run: "#index"
      inputs:
        - { id: file, source: "#main/infile" }
      outputs:
        - id: result

    - id: search
      run: "#search"
      inputs:
        - { id: file, source: "#main/index/result" }
        - { id: term, source: "#main/term" }
      outputs:
        - id: result