#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: "cwl:draft-3.dev1"
requirements:
  - "@import": node-engine.cwl
  - "@import": schemadef-type.yml

inputs:
    - id: "#hello"
      type: "schemadef-type.yml#HelloType"
      inputBinding:
        valueFrom:
          engine: node-engine.cwl
          script: |
            {
            return $self.a + "/" + $self.b;
            }

outputs:
    - id: "#output"
      type: File
      outputBinding:
        glob: output.txt

stdout: output.txt
baseCommand: echo
