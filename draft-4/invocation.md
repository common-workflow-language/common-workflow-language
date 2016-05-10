# Running a Command

To accommodate the enormous variety in syntax and semantics for input, runtime
environment, invocation, and output of arbitrary programs, a CommandLineTool
defines an "input binding" that describes how to translate abstract input
parameters to an concrete program invocation, and an "output binding" that
describes how to generate output parameters from program output.

## Input binding

The tool command line is built by applying command line bindings to the
input object.  Bindings are listed either as part of an [input
parameter](#CommandInputParameter) using the `inputBinding` field, or
separately using the `arguments` field of the CommandLineTool.

The algorithm to build the command line is as follows.  In this algorithm,
the sort key is a list consisting of one or more numeric or string
elements.  Strings are sorted lexicographically based on UTF-8 encoding.

  1. Collect `CommandLineBinding` objects from `arguments`.  Assign a sorting
  key `[position, i]` where `position` is
  [`CommandLineBinding.position`](#CommandLineBinding) and `i`
  is the index in the `arguments` list.

  2. Collect `CommandLineBinding` objects from the `inputs` schema and
  associate them with values from the input object.  Where the input type
  is a record, array, or map, recursively walk the schema and input object,
  collecting nested `CommandLineBinding` objects and associating them with
  values from the input object.

  3. Create a sorting key by taking the value of the `position` field at
  each level leading to each leaf binding object.  If `position` is not
  specified, it is not added to the sorting key.  For bindings on arrays
  and maps, the sorting key must include the array index or map key
  following the position.  If and only if two bindings have the same sort
  key, the tie must be broken using the ordering of the field or parameter
  name immediately containing the leaf binding.

  4. Sort elements using the assigned sorting keys.  Numeric entries sort
  before strings.

  5. In the sorted order, apply the rules defined in
  [`CommandLineBinding`](#CommandLineBinding) to convert bindings to actual
  command line elements.

  6. Insert elements from `baseCommand` at the beginning of the command
  line.

## Runtime environment

All files listed in the input object must be made available in the runtime
environment.  The implementation may use a shared or distributed file
system or transfer files via explicit download.  Implementations may choose
not to provide access to files not explicitly specified in the input object
or process requirements.

Output files produced by tool execution must be written to the **designated
output directory**.  The initial current working directory when executing
the tool must be the designated output directory.

Files may also be written to the **designated temporary directory**.  This
directory must be isolated and not shared with other processes.  Any files
written to the designated temporary directory may be automatically deleted by
the workflow platform immediately after the tool terminates.

For compatibility, files may be written to the **system temporary directory**
which must be located at `/tmp`.  Because the system temporary directory may be
shared with other processes on the system, files placed in the system temporary
directory are not guaranteed to be deleted automatically.  Correct tools must
clean up temporary files written to the system temporary directory.  A tool
must not use the system temporary directory as a backchannel communication with
other tools.  It is valid for the system temporary directory to be the same as
the designated temporary directory.

When executing the tool, the tool must execute in a new, empty environment
with only the environment variables described below; the child process must
not inherit environment variables from the parent process except as
specified or at user option.

  * `HOME` must be set to the designated output directory.
  * `TMPDIR` must be set to the designated temporary directory.
    when the tool invocation and output collection is complete.
  * `PATH` may be inherited from the parent process, except when run in a
    container that provides its own `PATH`.
  * Variables defined by [EnvVarRequirement](#EnvVarRequirement)
  * The default environment of the container, such as when using
    [DockerRequirement](#DockerRequirement)

An implementation may forbid the tool from writing to any location in the
runtime environment file system other than the designated temporary directory,
system temporary directory, and designated output directory.  An implementation
may provide read-only input files, and disallow in-place update of input files.
The designated temporary directory, system temporary directory and designated
output directory may each reside on different mount points on different file
systems.

An implementation may forbid the tool from directly accessing network
resources.  Correct tools must not assume any network access.  Future versions
of the specification may incorporate optional process requirements that
describe the networking needs of a tool.

The `runtime` section available in [parameter references](#Parameter_references)
and [expressions](#Expressions) contains the following fields.  As noted
earlier, an implementation may perform deferred resolution of runtime fields by providing
opaque strings for any or all of the following fields; parameter references
and expressions may only use the literal string value of the field and must
not perform computation on the contents.

  * `runtime.outdir`: an absolute path to the designated output directory
  * `runtime.tmpdir`: an absolute path to the designated temporary directory
  * `runtime.cores`:  number of CPU cores reserved for the tool process
  * `runtime.ram`:    amount of RAM in mebibytes (2**20) reserved for the tool process
  * `runtime.outdirSize`: reserved storage space available in the designated output directory
  * `runtime.tmpdirSize`: reserved storage space available in the designated temporary directory

See [ResourceRequirement](#ResourceRequirement) for details on how to
describe the hardware resources required by a tool.

The standard input stream and standard output stream may be redirected as
described in the `stdin` and `stdout` fields.

## Execution

Once the command line is built and the runtime environment is created, the
actual tool is executed.

The standard error stream and standard output stream (unless redirected by
setting `stdout`) may be captured by platform logging facilities for
storage and reporting.

Tools may be multithreaded or spawn child processes; however, when the
parent process exits, the tool is considered finished regardless of whether
any detached child processes are still running.  Tools must not require any
kind of console, GUI, or web based user interaction in order to start and
run to completion.

The exit code of the process indicates if the process completed
successfully.  By convention, an exit code of zero is treated as success
and non-zero exit codes are treated as failure.  This may be customized by
providing the fields `successCodes`, `temporaryFailCodes`, and
`permanentFailCodes`.  An implementation may choose to default unspecified
non-zero exit codes to either `temporaryFailure` or `permanentFailure`.

## Output binding

If the output directory contains a file named "cwl.output.json", that file
must be loaded and used as the output object.  Otherwise, the output object
must be generated by walking the parameters listed in `outputs` and
applying output bindings to the tool output.  Output bindings are
associated with output parameters using the `outputBinding` field.  See
[`CommandOutputBinding`](#CommandOutputBinding) for details.
