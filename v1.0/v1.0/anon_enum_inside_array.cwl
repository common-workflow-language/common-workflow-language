cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  first:
    type:
      type: record
      fields:
        species:
            - type: enum
              symbols: [homo_sapiens, mus_musculus]
            - "null"
  second:
    type:
      - "null"
      - type: enum
        symbols: [homo_sapiens, mus_musculus]
baseCommand: echo
arguments:
  - prefix: first
    valueFrom: $(inputs.first.species)
  - prefix: second
    valueFrom: $(inputs.second)
outputs:
  result: stdout

