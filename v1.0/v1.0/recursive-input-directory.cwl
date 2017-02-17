cwlVersion: v1.0
class: CommandLineTool
requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.input_dir)
        entryname: work_dir
        writable: true
baseCommand:
 -  bash
 - '-c'
 - 'touch work_dir/testresult;
    touch work_dir/e;
    if [ ! -w work_dir ]; then echo work_dir not writable >> work_dir/testresult; fi;
    if [ -L work_dir ]; then echo work_dir is a symlink >> work_dir/testresult; fi;
    if [ ! -w work_dir/a ]; then echo work_dir/a not writable >> work_dir/testresult; fi;
    if [ -L work_dir/a ]; then echo work_dir/a is a symlink >> work_dir/testresult; fi;
    if [ ! -w work_dir/c ]; then echo work_dir/c not writable >> work_dir/testresult; fi;
    if [ -L work_dir/c ]; then echo work_dir/c is a symlink >> work_dir/testresult; fi;
    if [ ! -w work_dir/c/d ]; then echo work_dir/c/d not writable >> work_dir/testresult; fi;
    if [ -L work_dir/c/d ]; then echo work_dir/c/d is a symlink >> work_dir/testresult; fi;
    if [ ! -w work_dir/e ]; then echo work_dir/e not writable >> work_dir/testresult; fi;
    if [ -L work_dir/e ]; then echo work_dir/e is a symlink >> work_dir/testresult; fi;'

inputs:
  input_dir: Directory
outputs:
  output_dir:
    type: Directory
    outputBinding:
      glob: work_dir