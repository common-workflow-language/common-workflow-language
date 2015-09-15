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
    "outputs": [
        {
            "id": "#output_txt",
            "type": "File",
            "outputBinding": {
              "glob": "output.txt"
              }
        }
    ],
    "baseCommand": "cat",
    "stdout": "output.txt",
    "stdin": {
      "engine": "cwl:JsonPointer",
      "script": "job/file1/path"
      }
}
