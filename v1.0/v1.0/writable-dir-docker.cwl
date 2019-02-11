cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entryname: emptyWritableDir
        entry: "$({class: 'Directory', listing: []})"
        writable: true

hints:
  - class: DockerRequirement
    dockerPull: alpine
  - class: ResourceRequirement
    ramMin: 8

inputs: []
outputs:
  out:
    type: Directory
    outputBinding:
      glob: emptyWritableDir
arguments: [touch, emptyWritableDir/blurg]
