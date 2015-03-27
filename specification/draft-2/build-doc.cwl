#!/usr/bin/env cwl-runner

class: Workflow
inputs:
  - id: "#spec"
    type: File
  - id: "#schema"
    type: File
  - id: "#script"
    type: File
outputs:
  - id: "#doc"
    type: File
    connect: {source: "#doc.html"}
steps:
  - class: CommandLineTool
    id: "#step1"
    requirements:
      - class: DockerRequirement
        dockerFile: |
          FROM debian:8
          RUN apt-get update && apt-get install -qq nodejs npm python-pip
          RUN pip install cwltool
          RUN npm install avrodoc -g && cd /usr/bin && ln -s nodejs node
        dockerImageId: debian/avrodoc
    inputs:
      - id: "#step1/spec"
        type: File
        connect: {source: "#spec"}
        commandLineBinding: {position: 3}
      - id: "#step1/schema"
        type: File
        connect: {source: "#schema"}
        commandLineBinding: {position: 2}
      - id: "#step1/script"
        type: File
        connect: {source: "#script"}
        commandLineBinding: {position: 1}
    outputs:
      - id: "#step1/avsc"
        type: File
        outputBinding:
          glob: in.avsc
    baseCommand: ["python"]
  - class: CommandLineTool
    requirements:
      - class: DockerRequirement
        dockerImageId: debian/avrodoc
    inputs:
      - id: "#step2/avsc"
        type: File
        connect: {source: "#step1/avsc"}
        commandLineBinding: {}
    outputs:
      - id: "#doc.html"
        type: File
    baseCommand: ["avrodoc"]
    stdout: {ref: "#doc.html"}
