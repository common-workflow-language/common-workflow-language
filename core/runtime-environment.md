# Runtime Environment

Every execution of every tool will have set its own separate working directory. Executor will  contain a file named `input.json`.

Tool should create its output files inside its working directory. Exception to this rule is when tool is creating accompanying file to its input file, such as index file. In that case a tool can choose to create its output in the same folder as input file.

### Input file format


