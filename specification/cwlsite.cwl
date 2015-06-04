#!/usr/bin/env cwl-runner

class: Workflow
inputs:
  - { id: "#main_index_in", type: File }

outputs:
  - { id: "#draft2_spec", type: File, connect: {source: "#spec.index.html" } }
  - { id: "#main_index", type: File, connect: {source: "#readme.index.html" } }

hints:
  - class: DockerRequirement
    dockerImageId: commonworkflowlanguage/cwltool_pip
    dockerFile: |
      FROM debian:8
      RUN apt-get update -qq && apt-get install -qqy python-pip
      RUN pip install cwltool

steps:
  - id: "#spec"
    inputs: []
    outputs:
      - { id: "#spec.index.html", param: "#_spec.index.html" }
    run:
      class: CommandLineTool
      inputs: []
      outputs:
        - id: "#_spec.index.html"
          type: File
          outputBinding: { glob: draft-2/index.html }
      baseCommand: ["cwltool", "--print-spec"]
      stdout: draft-2/index.html

  - id: "#readme"
    inputs:
      - { param: "#readme.in", connect: {source: "#main_index_in" } }
    outputs:
      - { id: "#readme.index.html", param: "#_readme.index.html" }
    run:
      class: CommandLineTool
      inputs:
        - id: "#readme.in"
          type: File
          inputBinding: { position: 2 }
        - id: "#readme.generate.py"
          type: File
          default:
            class: File
            path: "generate.py"
          inputBinding:
            { position: 1 }
      outputs:
        - id: "#_readme.index.html"
          type: File
          outputBinding: { glob: index.html }
      baseCommand: [python]
      stdout: index.html
