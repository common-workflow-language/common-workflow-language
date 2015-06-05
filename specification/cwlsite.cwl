#!/usr/bin/env cwl-runner

- id: "#makedoc"
  class: CommandLineTool
  inputs:
    - id: "#makedoc.source"
      type: File
      inputBinding: {position: 1}
    - id: "#makedoc.title"
      type: ["null", string]
      inputBinding: {position: 2}
    - id: "#makedoc.target"
      type: string
  outputs:
    - id: "#makedoc.out"
      type: File
      outputBinding:
        glob:
          engine: "cwl:JsonPointer"
          script: "job/makedoc.target"
  baseCommand: [python, "-mcwltool.avro_ld.makedoc"]
  stdout:
    engine: "cwl:JsonPointer"
    script: "job/makedoc.target"

- id: "#strip_leading_lines"
  class: CommandLineTool
  inputs:
    - id: "#strip_leading_lines.in"
      type: File
      inputBinding: {}
    - id: "#strip_leading_lines.count"
      type: int
      inputBinding:
        prefix: "-n+"
        separate: false
  outputs:
    - id: "#strip_leading_lines.out"
      type: File
      outputBinding:
        glob: "_tail_tmp.txt"
  baseCommand: ["tail", "-n+3"]
  stdout: "_tail_tmp.txt"

- id: "#main"
  class: Workflow
  inputs:
    - id: "#main_index_in"
      type: File
    - id: "#main_index_target"
      type: string
    - id: "#main_title"
      type: string
    - id: "#main_index_strip_lines"
      type: int
      default: 4

    - id: "#cwl_schema_in"
      type: File
    - id: "#cwl_schema_target"
      type: string

  outputs:
    - { id: "#draft2_spec", type: File, connect: {source: "#spec.index.html" } }
    - { id: "#main_index", type: File, connect: {source: "#readme.index.html" } }

  hints:
    - class: DockerRequirement
      dockerImageId: commonworkflowlanguage/cwltool_module
  steps:
  - id: "#spec"
    inputs:
      - { param: "#makedoc.source", connect: { source: "#cwl_schema_in" } }
      - { param: "#makedoc.target", connect: { source: "#cwl_schema_target" } }
    outputs:
      - { id: "#spec.index.html", param: "#makedoc.out" }
    run: {import: "#makedoc"}

  - id: "#strip_lines"
    inputs:
      - { param: "#strip_leading_lines.in", connect: {source: "#main_index_in" } }
      - { param: "#strip_leading_lines.count", connect: {source: "#main_index_strip_lines" } }
    outputs:
      - { id: "#strip_lines.out", param: "#strip_leading_lines.out" }
    run:  {import: "#strip_leading_lines"}

  - id: "#readme"
    inputs:
      - { param: "#makedoc.source", connect: {source: "#strip_lines.out" } }
      - { param: "#makedoc.target", connect: {source: "#main_index_target" } }
      - { param: "#makedoc.title", connect: {source: "#main_title" } }
    outputs:
      - { id: "#readme.index.html", param: "#makedoc.out" }
    run:  {import: "#makedoc"}
