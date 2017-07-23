class: CommandLineTool
cwlVersion: v1.0
hints:
  - class: DockerRequirement
    dockerPull: python:2-slim
requirements:
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.infile)
        entryname: bob.txt
        writable: true
inputs:
  infile: File
outputs:
  outfile:
    type: File
    outputBinding:
      glob: bob.txt
baseCommand: "python2"
arguments:
  - "-c"
  - |
    f = open("bob.txt", "r+")
    f.seek(8)
    f.write("Bob.    ")
    f.close()
