#!/usr/bin/env cwl-runner
{
    "@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json",
    "class": "ExpressionTool",
    "inputs": [{
        "id": "#file1",
        "type": "File",
        "loadContents": true
    }],
    "outputs": [{
        "id": "#output",
        "type": "int"
    }],
    "script": {
        "class": "JavascriptExpression",
        "script": "{return {'output': parseInt($job.file1.contents)};}"
    }
}
