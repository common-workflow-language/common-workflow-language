cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
requirements:
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.input_dir)
        entryname: work_dir
        writable: true
  ShellCommandRequirement: {}
stdout: output.txt
arguments:
 - shellQuote: false
   valueFrom: |
    touch work_dir/e;
    if [ ! -w work_dir ]; then echo work_dir not writable; fi;
    if [ -L work_dir ]; then echo work_dir is a symlink; fi;
    if [ ! -w work_dir/a ]; then echo work_dir/a not writable; fi;
    if [ -L work_dir/a ]; then echo work_dir/a is a symlink; fi;
    if [ ! -w work_dir/c ]; then echo work_dir/c not writable; fi;
    if [ -L work_dir/c ]; then echo work_dir/c is a symlink; fi;
    if [ ! -w work_dir/c/d ]; then echo work_dir/c/d not writable; fi;
    if [ -L work_dir/c/d ]; then echo work_dir/c/d is a symlink; fi;
    if [ ! -w work_dir/e ]; then echo work_dir/e not writable; fi;
    if [ -L work_dir/e ]; then echo work_dir/e is a symlink ; fi;
inputs:
  input_dir: Directory
outputs:
  output_dir:
    type: Directory
    outputBinding:
      glob: work_dir
  test_result:
    type: stdout
