#!/usr/bin/env cwl-runner
$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/
$schemas:
  - foaf.rdf
  - dcterms.rdf

cwlVersion: cwl:draft-3
class: CommandLineTool
description: "Print the contents of a file to stdout using 'cat' running in a docker container."

dct:creator:
  id: "http://orcid.org/0000-0003-3566-7705"
  class: foaf:Person
  foaf:name: Peter Amstutz
  foaf:mbox: "mailto:peter.amstutz@curoverse.com"

hints:
  - class: DockerRequirement
    dockerPull: debian:wheezy
inputs:
  - id: file1
    type: File
    inputBinding: {position: 1}
  - id: numbering
    type: ["null", boolean]
    inputBinding:
      position: 0
      prefix: -n
outputs: []
baseCommand: cat
