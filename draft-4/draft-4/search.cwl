cwlVersion: cwl:draft-4.dev1
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
    file:  File
    index.py:
      type: File
      default:
        class: File
        path: index.py
      inputBinding:
        position: 0
  outputs:
    result:
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
    file:
      type: File
      inputBinding:
        position: 1
      secondaryFiles:
        - ".idx1"
        - "^.idx2"
        - '$(self.path+".idx3")'
        - '$({"path": self.path+".idx4", "class": "File"})'
        - '${ return self.path+".idx5"; }'
    search.py:
      type: File
      default:
        class: File
        path: search.py
      inputBinding:
        position: 0
    term:
      type: string
      inputBinding:
        position: 2
  outputs:
    result:
      type: File
      outputBinding:
        glob: result.txt
  stdout: result.txt

- id: main
  class: Workflow
  inputs:
    infile: File
    term: string
  outputs:
    outfile:
      type: File
      source: "#main/search/result"
    indexedfile:
      type: File
      source: "#main/index/result"

  steps:
    index:
      run: "#index"
      in:
        file: "#main/infile"
      out: [result]

    search:
      run: "#search"
      in:
        file: "#main/index/result"
        term: "#main/term"
      out: [result]