# Common workflow language conformance test suite

This is designed to test conformance of an implementation of the common
workflow language tool description language.  The script "conformance_test.py"
accepts a path to a tool executable supplied on the command line and goes
through each test case defined in "conformance_test.json".

For example, to run the conformance test against the "cwltool" reference
implementation:

```
$ ./conformance_test.py ../reference/cwltool/main.py
Test [1/1]
All tests passed
```

The "conformance_test" script runs the tool with a specific command line
format. The tool must output a json object on standard output consisting of the
command line arguments in "args".  If specified in the tool description, it
must also include standard input redirection "stdin" and standard output
redirection "stdout".

An example of a single test invocation:

```
$ ../reference/cwltool/main.py --conformance-test ../examples/bwa-mem-tool.json ../examples/bwa-mem-job.json
{"args": ["bwa", "mem", "-t4", "-m", "3", "-I1,2,3,4", "./rabix/tests/test-files/chr20.fa", "./rabix/tests/test-files/example_human_Illumina.pe_1.fastq", "./rabix/tests/test-files/example_human_Illumina.pe_2.fastq"], "stdout": "output.sam"}
```

## Testing multiple tools

The "run_test.sh" script runs the conformance test suite across multiple tools.
Specify the path for each tool to test on the command line.

```
$ ./run_test.sh CWLTOOL=../reference RABIX=$HOME/work/rabix/rabix

--- Running cwltool tests ---
Test [1/1]
All tests passed

--- Running rabix/cliche tests ---
Test [1/1]
All tests passed

All tool tests succeeded
```
