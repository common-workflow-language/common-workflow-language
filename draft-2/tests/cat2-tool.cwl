#!/usr/bin/env cwl-runner
{
    "class": "CommandLineTool",
    "description": "Print the contents of a file to stdout using 'cat' running in a docker container.",
    "hints": [
        {
          "class": "DockerRequirement",
          "dockerPull": "debian:wheezy"
        }
    ],
    "inputs": [
        {
            "id": "#file1",
            "type": "File"
        }
    ],
    "outputs": [],
    "baseCommand": "cat",
    "stdin": {
      "engine": "cwl:JsonPointer",
      "script": "job/file1/path"
      }
}
