#!/usr/bin/env cwl-runner

class: ExpressionTool
cwlVersion: v1.0
requirements:
  - class: InlineJavascriptRequirement

inputs:
  size: int
outputs: { lit: File }
expression: |
  ${
     var contents = "a".repeat(inputs.size);
     return { "lit": { "class": "File", "basename": "lit", "contents": contents } };
  }
