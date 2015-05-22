#!/usr/bin/env cwl-runner
{
    "@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json",
    "class": "CommandLineTool",
    "inputs": [{
        "id": "#file1",
        "type": "File"
    }],
    "outputs": [{
        "id": "#output",
        "type": "File",
        "outputBinding": {
          "glob": "output"
        }
    }],
    "stdin": {
      "class": "Expression",
      "engine": "JsonPointer",
      "script": "job/file1/path"
    },
    "stdout": "output",
    "baseCommand": ["wc"]
}