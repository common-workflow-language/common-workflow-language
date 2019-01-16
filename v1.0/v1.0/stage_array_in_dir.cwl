class: CommandLineTool
cwlVersion: v1.0
baseCommand:
  - ls
  - staged
inputs:
  - id: infiles
    type: File[]
outputs:
  - id: outfile
    type: File
    outputBinding:
      glob: staged/whale.txt
requirements:
  - class: InitialWorkDirRequirement
    listing:
      - entry: >-
          ${ return { 'class': 'Directory', 'listing': inputs.infiles,
          'basename': 'staged'} }
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerPull: 'debian:stretch-slim'
