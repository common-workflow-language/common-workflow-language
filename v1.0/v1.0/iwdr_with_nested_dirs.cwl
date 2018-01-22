#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow

inputs: []
outputs:
  ya_empty:
    type: File
    outputSource: second/ya

steps:
  first:
    run:
      class: CommandLineTool
      baseCommand: [ mkdir, -p, deeply/nested/dir/structure ]
      inputs: []
      outputs:
        deep_dir:
          type: Directory
          outputBinding: { glob: deeply }
    in: {}
    out: [ deep_dir ]

  second:
    run:
      class: CommandLineTool
      baseCommand: [ touch, deeply/nested/dir/structure/ya ]
      requirements:
        InitialWorkDirRequirement:
          listing:
            - entry: $(inputs.dir)
              writable: true
      inputs:
        dir: Directory
      outputs:
        ya:
          type: File
          outputBinding: { glob: deeply/nested/dir/structure/ya }

    in: { dir: first/deep_dir }
    out: [ ya ]
