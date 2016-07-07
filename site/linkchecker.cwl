class: CommandLineTool
cwlVersion: v1.0
hints:
  DockerRequirement:
    dockerFile: |
      FROM debian:8
      RUN apt-get update && \
          DEBIAN_FRONTEND=noninteractive apt-get -yq install w3c-linkchecker \
    dockerImageId: commonworkflowlanguage/checklink
inputs:
  inp:
    type: File
    inputBinding: {position: 1}
  target: string
outputs:
  out:
    type: File
    outputBinding:
      glob: $(inputs.target)
      loadContents: true
      #outputEval: |
      #  ${
      #    return if (self.contents.length > 0) {
      #
      #    }
      #  }
baseCommand: checklink
arguments: ["-X(http.*|mailto:.*)", "-q"]
stdout: $(inputs.target)
