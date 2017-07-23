#!/usr/bin/env cwl-runner
{
    "class": "CommandLineTool",
    "cwlVersion": "v1.0",
    "doc": "Print the contents of a file to stdout using 'cat' running in a docker container.",
    "hints": [
        {
            "class": "DockerRequirement",
            "dockerPull": "python:2-slim"
        }
    ],
    "inputs": [
        {
            "id": "file1",
            "type": "File",
            "inputBinding": {"position": 1}
        },
        {
            "id": "numbering",
            "type": ["null", "boolean"],
            "inputBinding": {
                "position": 0,
                "prefix": "-n"
            }
        },
        {
        id: "args.py",
        type: File,
        default: {
          class: File,
          location: args.py
        },
        inputBinding: {
          position: -1
        }
      }
    ],
    "outputs": [{"id": "args", "type": "string[]"}],
    "baseCommand": "python",
    "arguments": ["cat"]
}
