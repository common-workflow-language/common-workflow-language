#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow
inputs: []
outputs:
  inputs_review:
    type: File
    outputSource: evaluate_inputs/inputs_review
steps:
  record_inputs:
    run:
      class: CommandLineTool
      inputs:
        a_string:
          type: string
          default: z
        a_string_array:
          type: string[]
          default: [a, b, c]
        a_true:
          type: boolean
          default: true
        an_array_of_trues:
          type: boolean[]
          default: [true, true, true]
        an_array_of_falses:
          type: boolean[]
          default: [false, false, false]
        an_array_of_mixed_booleans:
          type: boolean[]
          default: [false, true, false]
        an_int:
          type: int
          default: 42
        an_array_of_ints:
          type: int[]
          default: [42, 23]
        a_long:
          type: long
          default: 4147483647
        an_array_of_longs:
          type: long[]
          default: [4147483647, -4147483647]
        a_float:
          type: float
          default: 4.2
        an_array_of_floats:
          type: float[]
          default: [2.3, 4.2]
        a_double:
          type: double
          default: 1000000000000000000000000000000000000000000
        an_array_of_doubles:
          type: double[]
          default:
            - 1000000000000000000000000000000000000000000
            - -1000000000000000000000000000000000000000000
      arguments:
       - '{"inputs":$(inputs)}'
      outputs:
        inputs_dump: stdout
      baseCommand: echo
      stdout: inputs.json
    in: []
    out: [inputs_dump]
  evaluate_inputs:
    run:
      class: CommandLineTool
      hints:
        DockerRequirement:
          dockerPull: everpeace/curl-jq
      inputs:
        inputs_json:
          type: File
          inputBinding:
            position: 2
      stdout: inputs_review.txt
      outputs:
       inputs_review: stdout
      baseCommand: jq
      arguments:
       - valueFrom: >
          .inputs == { "a_string": "z", "a_string_array": ["a", "b", "c"],
                       "a_true": true, "an_array_of_trues": [true, true, true],
                       "an_array_of_falses": [false, false, false],
                       "an_array_of_mixed_booleans": [false, true, false],
                       "an_int": 42, "an_array_of_ints": [42, 23],
                       "a_long": 4147483647,
                       "an_array_of_longs": [4147483647, -4147483647],
                       "a_float": 4.2, "an_array_of_floats": [2.3,4.2],
                       "a_double": 1000000000000000000000000000000000000000000,
                       "an_array_of_doubles": [1000000000000000000000000000000000000000000,-1000000000000000000000000000000000000000000]}
         position: 1
    in: { inputs_json: record_inputs/inputs_dump }
    out: [ inputs_review ]
      

