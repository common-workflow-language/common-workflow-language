#!/usr/bin/env cwl-runner
{
    "class": "CommandLineTool",
    "inputs": [{
        "id": "#file1",
        "datatype": "File"
    }],
    "outputs": [{
        "id": "#output",
        "datatype": "File",
        "outputBinding": {
          "glob": "output"
        }
    }],
    "stdin": {
      "engine": "JsonPointer",
      "script": "job/file1/path"
    },
    "stdout": "output",
    "baseCommand": ["wc"]
}