#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0

requirements:
  InlineJavascriptRequirement: {}

inputs:
  i: int

outputs:
  o:
    type: int
    outputSource: step3/o

steps:
  step1:
    in:
      i: i
    out: [o]
    run:
      class: ExpressionTool
      inputs:
        i:
          type: int
      outputs:
        o:
          type: int[]
      expression: >
        ${return {'o': Array.apply(null, {length: inputs.i}).map(Number.call, Number)};}
  step2:
    in:
      i:
        source: step1/o
    out: [o]
    run:
      class: ExpressionTool
      inputs:
        i:
          type: int[]
      outputs:
        o:
          type: int[]
      expression: >
        ${return {'o': inputs.i.map(function(x) { return (x + 1) * 2; })};}
  step3:
    in:
      i:
        source: step2/o
    out: [o]
    run:
      class: ExpressionTool
      inputs:
        i:
          type: int[]
      outputs:
        o:
          type: int
      expression: >
        ${return {'o': inputs.i.reduce(function(a, b) { return a + b; })};}
