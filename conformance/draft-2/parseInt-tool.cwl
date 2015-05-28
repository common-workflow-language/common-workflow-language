#!/usr/bin/env cwl-runner
{
    "class": "ExpressionTool",
    "requirements": [{
      id: "node-engine.cwl"
    }],
    "inputs": [{
        "id": "#file1",
        "datatype": "File",
        "loadContents": true
    }],
    "outputs": [{
        "id": "#output",
        "datatype": "int"
    }],
    "expression": {
        "engine": node-engine.cwl,
        "script": "{return {'output': parseInt($job.file1.contents)};}"
    }
}
