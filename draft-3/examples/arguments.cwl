cwlVersion: cwl:draft-3
class: CommandLineTool
label: Example trivial wrapper for Java 7 compiler
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
