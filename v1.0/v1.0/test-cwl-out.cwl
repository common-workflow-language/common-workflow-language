class: CommandLineTool
cwlVersion: v1.0
requirements:
  - class: ShellCommandRequirement
hints:
  ResourceRequirement:
    ramMin: 8
  DockerRequirement:
    dockerPull: "debian:stretch-slim"

inputs: []

outputs:
  - id: foo
    type: File

arguments:
   - valueFrom: >
       echo foo > foo && echo '{"foo": {"path": "$(runtime.outdir)/foo", "class": "File"} }' > cwl.output.json
     shellQuote: false
