#!/usr/bin/env cwl-runner
{
    "@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json",
    "class": "CommandLineTool",
    "requirements": [
        {
            "class": "MemoryRequirement",
            "total_mem": 5000
        },
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
            "type": "File",
            "commandLineBinding": {
                "position": 2
            }
        },
        {
            "id": "#reads",
            "type": {
                "type": "array",
                "items": "File",
                "commandLineBinding": {
                    "position": 3
                }
            }
        },
        {
            "id": "#minimum_seed_length",
            "type": "int",
            "commandLineBinding": {
                "position": 1,
                "prefix": "-m"
            }
        },
        {
            "id": "#min_std_max_min",
            "type": {
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
            "type": "File",
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
