class: CommandLineTool
cwlVersion: v1.1.0-dev1
requirements:
  - class: ShellCommandRequirement
hints:
  DockerRequirement:
    dockerPull: "debian:stretch-slim"

inputs: []

outputs:
  - id: foo
    type: File

arguments:
   - valueFrom: >
       echo foo > foo && echo '{"foo": {"location": "file://$(runtime.outdir)/foo", "class": "File"} }' > cwl.output.json
     shellQuote: false
