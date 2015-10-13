class: CommandLineTool
description: "Reverse each line using the `rev` command"
requirements:
  - class: DockerRequirement
    dockerImageId: dnd
    dockerFile: |
      FROM ubuntu:14.04
      MAINTAINER peter.amstutz@curoverse.com

      RUN apt-get update -qq && apt-get install -qqy \
      apt-transport-https \
      ca-certificates \
      curl \
      lxc \
      iptables \
      python-setuptools

      # Install Docker from Docker Inc. repositories.
      RUN curl -sSL https://get.docker.com/ubuntu/ | sh

  - class: DockerSocketRequirement
inputs: []
outputs:
  - id: "#output"
    type: File
    outputBinding:
      glob: output.txt
baseCommand: [docker, version]
stdout: output.txt