cwlVersion: v1.0
class: CommandLineTool
requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.input_dir)
        entryname: work_dir
        writable: true
baseCommand: [touch, work_dir/e]
inputs:
  input_dir: Directory
outputs:
  output_dir:
    type: Directory
    outputBinding:
      glob: work_dir