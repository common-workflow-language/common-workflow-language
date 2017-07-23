cwlVersion: v1.0
class: CommandLineTool
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entryname: emptyWritableDir
        writable: true
        entry: "$({class: 'Directory', listing: []})"
inputs: []
outputs:
  out:
    type: Directory
    outputBinding:
      glob: emptyWritableDir
arguments: [touch, emptyWritableDir/blurg]
