cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: javac
hints:
  - class: DockerRequirement
    dockerPull: java:7
baseCommand: javac
arguments:
  - prefix: "-d"
    valueFrom: $(runtime.outdir)
inputs:
  - id: src
    type: File
    inputBinding:
      position: 1
outputs:
  - id: classfile
    type: File
    outputBinding:
      glob: "*.class"
