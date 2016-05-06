class: CommandLineTool
cwlVersion: cwl:draft-4.dev1
requirements:
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: debian:wheezy

inputs: []

outputs:
  - id: foo
    type: File

baseCommand: []
arguments:
   - valueFrom: >
       echo foo > foo && echo '{"foo": {"path": "$(runtime.outdir)/foo", "class": "File"} }' > cwl.output.json
     shellQuote: false
