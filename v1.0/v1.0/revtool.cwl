#
# Simplest example command line program wrapper for the Unix tool "rev".
#
class: CommandLineTool
cwlVersion: v1.0
doc: "Reverse each line using the `rev` command"

# The "inputs" array defines the structure of the input object that describes
# the inputs to the underlying program.  Here, there is one input field
# defined that will be called "input" and will contain a "File" object.
#
# The input binding indicates that the input value should be turned into a
# command line argument.  In this example inputBinding is an empty object,
# which indicates that the file name should be added to the command line at
# a default location.
inputs:
  input:
    type: File
    inputBinding: {}

# The "outputs" array defines the structure of the output object that
# describes the outputs of the underlying program.  Here, there is one
# output field defined that will be called "output", must be a "File" type,
# and after the program executes, the output value will be the file
# output.txt in the designated output directory.
outputs:
  output:
    type: File
    outputBinding:
      glob: output.txt

# The actual program to execute.
baseCommand: rev

# Specify that the standard output stream must be redirected to a file called
# output.txt in the designated output directory.
stdout: output.txt
