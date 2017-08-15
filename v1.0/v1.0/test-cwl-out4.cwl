class: CommandLineTool
cwlVersion: v1.0
requirements:
  - class: ShellCommandRequirement
hints:
  DockerRequirement:
    dockerPull: "debian:wheezy"

inputs:
  file1: File

outputs:
  - id: foo
    type: File

arguments:
   - valueFrom: >
       echo '{"foo": {"path": "$(inputs.file1.path)", "class": "File"} }' > cwl.output.json
     shellQuote: false
