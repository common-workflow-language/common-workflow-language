class: CommandLineTool
cwlVersion: v1.0
hints:
  ResourceRequirement:
    ramMin: 8
requirements:
  - class: ShellCommandRequirement
inputs:
  irec:
    type:
      name: irec
      type: record
      fields:
      - name: ifoo
        type: File
        inputBinding:
          position: 2
      - name: ibar
        type: File
        inputBinding:
          position: 6
outputs:
  orec:
    type:
      name: orec
      type: record
      fields:
      - name: ofoo
        type: File
        outputBinding:
          glob: foo
      - name: obar
        type: File
        outputBinding:
          glob: bar
arguments:
  - {valueFrom: "cat", position: 1}
  - {valueFrom: "> foo", position: 3, shellQuote: false}
  - {valueFrom: "&&", position: 4, shellQuote: false}
  - {valueFrom: "cat", position: 5}
  - {valueFrom: "> bar", position: 7, shellQuote: false}
