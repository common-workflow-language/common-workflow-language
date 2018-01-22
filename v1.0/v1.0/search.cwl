cwlVersion: v1.0
$graph:
- id: index
  class: CommandLineTool
  baseCommand: python
  arguments:
    - valueFrom: input.txt
      position: 1
  requirements:
    - class: InitialWorkDirRequirement
      listing:
        - entryname: input.txt
          entry: $(inputs.file)
    - class: InlineJavascriptRequirement
  hints:
    - class: DockerRequirement
      dockerPull: python:2-slim

  inputs:
    file:  File
    secondfile:  File
    index.py:
      type: File
      default:
        class: File
        location: index.py
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
        - '$(self.basename).idx3'
        - '${ return self.basename+".idx4"; }'
        - '$({"path": self.path+".idx5", "class": "File"})'
        - '$(self.nameroot).idx6$(self.nameext)'
        - '${ return [self.basename+".idx7", inputs.secondfile]; }'
        - "_idx8"

- id: search
  class: CommandLineTool
  baseCommand: python
  requirements:
    - class: InlineJavascriptRequirement
  hints:
    - class: DockerRequirement
      dockerPull: python:2-slim
  inputs:
    file:
      type: File
      inputBinding:
        position: 1
      secondaryFiles:
        - ".idx1"
        - "^.idx2"
        - '$(self.basename).idx3'
        - '${ return self.basename+".idx4"; }'
        - '$(self.nameroot).idx6$(self.nameext)'
        - '${ return [self.basename+".idx7"]; }'
        - "_idx8"
    search.py:
      type: File
      default:
        class: File
        location: search.py
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
    secondfile: File
    term: string
  outputs:
    outfile:
      type: File
      outputSource: search/result
    indexedfile:
      type: File
      outputSource: index/result

  steps:
    index:
      run: "#index"
      in:
        file: infile
        secondfile: secondfile
      out: [result]

    search:
      run: "#search"
      in:
        file: index/result
        term: term
      out: [result]
