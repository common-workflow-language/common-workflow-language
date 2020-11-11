class: CommandLineTool
cwlVersion: v1.0
baseCommand:
  - cp
  - staged/whale.txt
  - whale_copy.txt
inputs:
  - id: infiles
    type: File[]
outputs:
  - id: outfile
    type: File
    outputBinding:
      glob: whale_copy.txt
requirements:
  - class: InitialWorkDirRequirement
    listing:
      - entry: >-
          ${ return { 'class': 'Directory', 'listing': inputs.infiles,
          'basename': 'staged'} }
        writable: true
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerPull: 'debian:stretch-slim'
