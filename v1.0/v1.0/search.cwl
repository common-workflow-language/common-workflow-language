cwlVersion: v1.0
$graph:
- id: index
  class: CommandLineTool
  baseCommand: python2
  arguments:
    - valueFrom: input.txt
      position: 1
  requirements:
    - class: InitialWorkDirRequirement
      listing:
        - entryname: input.txt
          entry: $(inputs.file)
    - class: InlineJavascriptRequirement

  inputs:
    file:  File
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
        - '$(self.location+".idx3")'
        - '$({"location": self.location+".idx4", "class": "File"})'
        - '${ return self.location+".idx5"; }'

- id: search
  class: CommandLineTool
  baseCommand: python2
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
        - '$(self.location+".idx3")'
        - '$({"location": self.location+".idx4", "class": "File"})'
        - '${ return self.location+".idx5"; }'
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
        file: "#main/infile"
      out: [result]

    search:
      run: "#search"
      in:
        file: "#main/index/result"
        term: "#main/term"
      out: [result]
