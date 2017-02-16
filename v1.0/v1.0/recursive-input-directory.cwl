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
 - 'if [ ! -w work_dir ]; then echo not writable; fi;
   if [ -L work_dir ]; then echo dir is a symlink; fi;
   if [ ! -w work_dir/a ]; then echo not writable; fi;
   if [ -L work_dir/a ]; then echo dir is a symlink; fi;
   if [ ! -w work_dir/c ]; then echo not writable; fi;
   if [ -L work_dir/c ]; then echo dir is a symlink; fi;
   if [ ! -w work_dir/c/d ]; then echo not writable; fi;
   if [ -L work_dir/c/d ]; then echo dir is a symlink; fi;
   touch work_dir/e'
inputs:
  input_dir: Directory
outputs:
  output_dir:
    type: Directory
    outputBinding:
      glob: work_dir