#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8

requirements:
  - $import: schemadef-type.yml

inputs:
    - id: hello
      type: "schemadef-type.yml#HelloType"
      inputBinding:
        valueFrom: $(self.a)/$(self.b)

outputs:
    - id: output
      type: File
      outputBinding:
        glob: output.txt

stdout: output.txt
baseCommand: echo
