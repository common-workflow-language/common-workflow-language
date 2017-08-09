#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.0
inputs:
  file1: File
outputs:
  count_output: {type: int, outputSource: step1/count_output}
requirements:
  SubworkflowFeatureRequirement: {}
steps:
  step1:
    in: {file1: file1}
    out: [count_output]
    run:
      class: Workflow
      inputs:
        file1: File
      outputs:
        count_output: {type: int, outputSource: step2/count_output}
      steps:
        step1: {run: wc-tool.cwl, in: {file1: file1}, out: [output]}
        step2:
          in: {file1: step1/output}
          out: [count_output]
          run:
            class: Workflow
            inputs:
              file1: File
            outputs:
              count_output: {type: int, outputSource: step1/output}
            steps:
              step1: {run: parseInt-tool.cwl, in: {file1: file1}, out: [output]}
