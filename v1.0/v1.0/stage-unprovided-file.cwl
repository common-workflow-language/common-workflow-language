cwlVersion: v1.0
class: CommandLineTool

requirements: { InlineJavascriptRequirement: {} }

inputs:
  - id: infile
    type: File?
    inputBinding:
      prefix: -cfg
      valueFrom: $(self.basename)
  - id: "args.py"
    type: File
    default:
      class: File
      location: args.py
    inputBinding:
      position: -1

baseCommand: python

outputs:
- id: args
  type: string[]

