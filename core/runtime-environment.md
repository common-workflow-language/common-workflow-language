# Runtime Environment

Every execution of every tool will have set its own separate working directory. Executor will  contain a file named `job.json`.

Tool should create its output files inside its working directory. Exception to this rule is when tool is creating accompanying file to its input file, such as index file. In that case a tool can choose to create its output in the same folder as input file.

### Job order file format

Job order is a JSON file that contains an application ID, tool inputs, resources allocated for the job, and list of supported platform features.

Example:

```json
{
  "@context": "http://example.com/contexts/draft01/job"
  "app": "http://example.com/tools/mwa",
  "inputs": {
    "input1": {
      "path": "../files/input1.fasta",
      "size": 678599850,
      "checksum": "sha1$6809bc2706188b7b10d99d06fe4f175f8fe8061a",
      "metadata": {
        "fileType": "fasta"
      }
    }
  },
  "allocatedResources": {
    "cpu": 4,
    "memMB": 5000,
    "ports": [],
    "diskSpaceGB": 1000,
    "network": false
  },
  "platformFeatures": [
    "http://example.com/features/docker",
    "http://myplatform.com/features/vendor-feature"
  ]
}
```
