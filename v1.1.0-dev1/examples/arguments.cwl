cwlVersion: v1.1.0-dev1
class: CommandLineTool
label: Example trivial wrapper for Java 7 compiler
hints:
  DockerRequirement:
    dockerPull: java:7
baseCommand: javac
arguments: ["-d", $(runtime.outdir)]
inputs:
  src:
    type: File
    inputBinding:
      position: 1
outputs:
  classfile:
    type: File
    outputBinding:
      glob: "*.class"
