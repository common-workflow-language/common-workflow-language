#!/usr/bin/env cwl-runner

- id: "#makedoc"
  class: CommandLineTool
  inputs:
    - id: "#makedoc_source"
      type: File
      inputBinding: {position: 1}
    - id: "#makedoc_title"
      type: ["null", string]
      inputBinding: {position: 2}
    - id: "#makedoc_target"
      type: string
  outputs:
    - id: "#makedoc_out"
      type: File
      outputBinding:
        glob:
          engine: "cwl:JsonPointer"
          script: "job/makedoc_target"
  baseCommand: [python, "-mcwltool.avro_ld.makedoc"]
  stdout:
    engine: "cwl:JsonPointer"
    script: "job/makedoc_target"

- id: "#makecontext"
  class: CommandLineTool
  inputs:
    - id: "#makecontext_target"
      type: string
  outputs:
    - id: "#makecontext_out"
      type: File
      outputBinding:
        glob:
          engine: "cwl:JsonPointer"
          script: "job/makecontext_target"
  baseCommand: [python, "-mcwltool", "--print-jsonld-context"]
  stdout:
    engine: "cwl:JsonPointer"
    script: "job/makecontext_target"


- id: "#strip_leading_lines"
  class: CommandLineTool
  inputs:
    - id: "#strip_leading_lines_in"
      type: File
      inputBinding: {}
    - id: "#strip_leading_lines_count"
      type: int
      inputBinding:
        prefix: "-n+"
        separate: false
  outputs:
    - id: "#strip_leading_lines_out"
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
    - id: "#cwl_context_target"
      type: string


  outputs:
    - { id: "#draft2_spec", type: File, source: "#spec.makedoc_out" }
    - { id: "#main_index", type: File, source: "#readme.makedoc_out" }
    - { id: "#main_context", type: File, source: "#context.makecontext_out" }

  hints:
    - class: DockerRequirement
      dockerPull: commonworkflowlanguage/cwltool_module
  steps:
  - id: "#spec"
    inputs:
      - { id: "#spec.makedoc_source", source: "#cwl_schema_in" }
      - { id: "#spec.makedoc_target", source: "#cwl_schema_target" }
    outputs:
      - { id: "#spec.makedoc_out" }
    run: {import: "#makedoc"}

  - id: "#context"
    inputs:
      - { id: "#context.makecontext_target", source: "#cwl_context_target"}
    outputs:
      - { id: "#context.makecontext_out"}
    run: {import: "#makecontext"}

  - id: "#strip_lines"
    inputs:
      - { id: "#strip_lines.strip_leading_lines_in", source: "#main_index_in" }
      - { id: "#strip_lines.strip_leading_lines_count", source: "#main_index_strip_lines" }
    outputs:
      - { id: "#strip_lines.strip_leading_lines_out" }
    run:  {import: "#strip_leading_lines"}

  - id: "#readme"
    inputs:
      - { id: "#readme.makedoc_source", source: "#strip_lines.strip_leading_lines_out" }
      - { id: "#readme.makedoc_target", source: "#main_index_target" }
      - { id: "#readme.makedoc_title", source: "#main_title" }
    outputs:
      - { id: "#readme.makedoc_out" }
    run:  {import: "#makedoc"}
