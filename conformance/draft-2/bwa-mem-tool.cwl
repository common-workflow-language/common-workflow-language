#!/usr/bin/env cwl-runner
{
    "@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json",
    "class": "CommandLineTool",
    "requirements": [
        {
            id: "node-engine.cwl"
        }
    ],
    "hints": [
        {
            "class": "DockerRequirement",
            "dockerPull": "images.sbgenomics.com/rabix/bwa",
            "dockerImageId": "9d3b9b0359cf"
        }
    ],
    "inputs": [
        {
            "id": "#reference",
            "datatype": "File",
            "commandLineBinding": {
                "position": 2
            }
        },
        {
            "id": "#reads",
            "datatype": {
                "type": "array",
                "items": "File",
                "commandLineBinding": {
                    "position": 3
                }
            }
        },
        {
            "id": "#minimum_seed_length",
            "datatype": "int",
            "commandLineBinding": {
                "position": 1,
                "prefix": "-m"
            }
        },
        {
            "id": "#min_std_max_min",
            "datatype": {
                "type": "array",
                "items": "int"
            },
            "commandLineBinding": {
                "itemSeparator": ",",
                "position": 1,
                "prefix": "-I"
            }
        }
    ],
    "outputs": [
        {
            "id": "#sam",
            "datatype": "File",
            "outputBinding": {
                "glob": "output.sam"
            }
        }
    ],
    "baseCommand": ["bwa", "mem"],
    "arguments": [
        {
            "valueFrom": {
                "engine": "node-engine.cwl",
                "script": "$job.allocatedResources.cpu"
            },
            "position": 1,
            "prefix": "-t"
        }
    ],
    "stdout": "output.sam"
}
