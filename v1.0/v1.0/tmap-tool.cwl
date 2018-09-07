#!/usr/bin/env cwl-runner
{
    "cwlVersion": "v1.0",

    "class": "CommandLineTool",
    "hints": [
        {
            "class": "DockerRequirement",
            "dockerPull": "python:2-slim"
        }
    ],
    "inputs": [
        {
            "id": "reads",
            "type": "File"
        },
        {
            "id": "stages",
            "inputBinding": {
                "position": 1
            },
            "type": {
                "type": "array",
                "items": "#Stage"
            }
        },
        {
        id: "#args.py",
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
    "outputs": [
        {
            "id": "sam",
            "outputBinding": {
                "glob": "output.sam"
            },
            "type": ["null", "File"]
        },
        {"id": "args", "type": "string[]"}
    ],
    "requirements": [
    {"class": "SchemaDefRequirement",
    "types": [
        {
            "fields": [
                {
                    "inputBinding": {
                        "position": 0
                    },
                    "name": "algo",
                    "type": {
                        "type": "enum",
                        "name": "JustMap1",
                        "symbols": ["map1"]
                    }
                },
                {
                    "name": "maxSeqLen",
                    "type": ["null", "int"],
                    "inputBinding": {
                        "prefix": "--max-seq-length",
                        "position": 2
                    }
                },
                {
                    "name": "minSeqLen",
                    "type": ["null", "int"],
                    "inputBinding": {
                        "prefix": "--min-seq-length",
                        "position": 2
                    }
                },
                {
                    "inputBinding": {
                        "position": 2,
                        "prefix": "--seed-length"
                    },
                    "name": "seedLength",
                    "type": ["null", "int"]
                }
            ],
            "name": "Map1",
            "type": "record"
        },
        {
            "fields": [
                {
                    "inputBinding": {
                        "position": 0
                    },
                    "name": "algo",
                    "type": {
                        "type": "enum",
                        "name": "JustMap2",
                        "symbols": ["map2"]
                    }
                },
                {
                    "name": "maxSeqLen",
                    "type": ["null", "int"],
                    "inputBinding": {
                        "prefix": "--max-seq-length",
                        "position": 2
                    }
                },
                {
                    "name": "minSeqLen",
                    "type": ["null", "int"],
                    "inputBinding": {
                        "prefix": "--min-seq-length",
                        "position": 2
                    }
                },
                {
                    "inputBinding": {
                        "position": 2,
                        "prefix": "--max-seed-hits"
                    },
                    "name": "maxSeedHits",
                    "type": ["null", "int"]
                }
            ],
            "name": "Map2",
            "type": "record"
        },
        {
            "fields": [
                {
                    "inputBinding": {
                        "position": 0
                    },
                    "name": "algo",
                    "type": {
                        "type": "enum",
                        "name": "JustMap3",
                        "symbols": ["map3"]
                    }
                },
                {
                    "name": "maxSeqLen",
                    "type": ["null", "int"],
                    "inputBinding": {
                        "prefix": "--max-seq-length",
                        "position": 2
                    }
                },
                {
                    "name": "minSeqLen",
                    "type": ["null", "int"],
                    "inputBinding": {
                        "prefix": "--min-seq-length",
                        "position": 2
                    }
                },
                {
                    "inputBinding": {
                        "position": 2,
                        "prefix": "--fwd-search"
                    },
                    "name": "fwdSearch",
                    "type": ["null", "boolean"]
                }
            ],
            "name": "Map3",
            "type": "record"
        },
        {
            "fields": [
                {
                    "inputBinding": {
                        "position": 0
                    },
                    "name": "algo",
                    "type": {
                        "type": "enum",
                        "name": "JustMap4",
                        "symbols": ["map4"]
                    }
                },
                {
                    "name": "maxSeqLen",
                    "type": ["null", "int"],
                    "inputBinding": {
                        "prefix": "--max-seq-length",
                        "position": 2
                    }
                },
                {
                    "name": "minSeqLen",
                    "type": ["null", "int"],
                    "inputBinding": {
                        "prefix": "--min-seq-length",
                        "position": 2
                    }
                },
                {
                    "inputBinding": {
                        "position": 2,
                        "prefix": "--seed-step"
                    },
                    "name": "seedStep",
                    "type": ["null", "int"]
                }
            ],
            "name": "Map4",
            "type": "record"
        },
        {
            "type": "record",
            "name": "Stage",
            "fields": [
                {
                    "inputBinding": {
                        "position": 0,
                        "prefix": "stage",
                        "separate": false
                    },
                    "name": "stageId",
                    "type": ["null", "int"]
                },
                {
                    "inputBinding": {
                        "position": 1,
                        "prefix": "-n"
                    },
                    "name": "stageOption1",
                    "type": ["null", "boolean"]
                },
                {
                    "inputBinding": {
                        "position": 2
                    },
                    "name": "algos",
                    "type": {
                        "type": "array",
                        "items": [
                            "#Map1",
                            "#Map2",
                            "#Map3",
                            "#Map4"
                        ]
                    }
                }
            ]
        }
    ]}],
    "baseCommand": "python",
    "arguments": ["tmap", "mapall"]
}
