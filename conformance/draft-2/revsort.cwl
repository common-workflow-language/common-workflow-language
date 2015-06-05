class: Workflow
description: "Reverse the lines in a document, then sort those lines."

inputs:
  - id: "#input"
    type: File
    description: "The input file to be processed."
  - id: "#reverse_sort"
    type: boolean
    default: true
    description: "If true, reverse (decending) sort"

outputs:
  - id: "#output"
    type: File
    connect: { source: "#sorted" }
    description: "The output with the lines reversed and sorted."

steps:
  - inputs:
      - { param: "revtool.cwl#input", connect: { source: "#input" } }
    outputs:
      - { id: "#reversed", param: "revtool.cwl#output" }
    run: { import: revtool.cwl }

  - inputs:
      - { param: "sorttool.cwl#input", connect: { source: "#reversed" } }
      - { param: "sorttool.cwl#reverse", connect: { source: "#reverse_sort" } }
    outputs:
      - { id: "#sorted", param: "sorttool.cwl#output" }
    run: { import: sorttool.cwl }
