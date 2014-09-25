# Tool Runtime Environment

Every execution MUST have its separate working directory.

Working directory MUST contain a file named `input.json`.

Tool SHOULD create its output files inside its working directory. Exception to this rule is when tool is creating accompanying file to its input file, such as index file. In that case a tool can choose to create its output in the same folder as input file.

### Input file format

