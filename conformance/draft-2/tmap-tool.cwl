#!/usr/bin/env cwl-runner
{
    "@context": "https://raw.githubusercontent.com/common-workflow-language/common-workflow-language/master/schemas/draft-2/cwl-context.json",
    "class": "CommandLineTool",

    "inputs": [
        {
            "id": "#reads",
            "type": "File"
        },
        {
            "id": "#stages",
            "commandLineBinding": {
                "position": 1
            },
            "type": {
                "type": "array",
                "items": "Stage"
            }
        }
    ],
    "outputs": [
        {
            "id": "#sam",
            "outputBinding": {
                "glob": "output.sam"
            },
            "type": "File"
        }
    ],
    "schemaDefs": [
        {
            "fields": [
                {
                    "commandLineBinding": {
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
                    "commandLineBinding": {
                        "prefix": "--max-seq-length",
                        "separator": " ",
                        "position": 2
                    }
                },
                {
                    "name": "minSeqLen",
                    "type": ["null", "int"],
                    "commandLineBinding": {
                        "prefix": "--min-seq-length",
                        "separator": " ",
                        "position": 2
                    }
                },
                {
                    "commandLineBinding": {
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
                    "commandLineBinding": {
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
                    "commandLineBinding": {
                        "prefix": "--max-seq-length",
                        "separator": " ",
                        "position": 2
                    }
                },
                {
                    "name": "minSeqLen",
                    "type": ["null", "int"],
                    "commandLineBinding": {
                        "prefix": "--min-seq-length",
                        "separator": " ",
                        "position": 2
                    }
                },
                {
                    "commandLineBinding": {
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
                    "commandLineBinding": {
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
                    "commandLineBinding": {
                        "prefix": "--max-seq-length",
                        "separator": " ",
                        "position": 2
                    }
                },
                {
                    "name": "minSeqLen",
                    "type": ["null", "int"],
                    "commandLineBinding": {
                        "prefix": "--min-seq-length",
                        "separator": " ",
                        "position": 2
                    }
                },
                {
                    "commandLineBinding": {
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
                    "commandLineBinding": {
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
                    "commandLineBinding": {
                        "prefix": "--max-seq-length",
                        "separator": " ",
                        "position": 2
                    }
                },
                {
                    "name": "minSeqLen",
                    "type": ["null", "int"],
                    "commandLineBinding": {
                        "prefix": "--min-seq-length",
                        "separator": " ",
                        "position": 2
                    }
                },
                {
                    "commandLineBinding": {
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
                    "commandLineBinding": {
                        "position": 0,
                        "prefix": "stage",
                        "separator": ""
                    },
                    "name": "stageId",
                    "type": ["null", "int"]
                },
                {
                    "commandLineBinding": {
                        "position": 1,
                        "prefix": "-n"
                    },
                    "name": "stageOption1",
                    "type": ["null", "boolean"]
                },
                {
                    "commandLineBinding": {
                        "position": 2
                    },
                    "name": "algos",
                    "type": {
                        "type": "array",
                        "items": [
                            "Map1",
                            "Map2",
                            "Map3",
                            "Map4"
                        ]
                    }
                }
            ]
        }
    ],
    "baseCommand": ["tmap", "mapall"],
    "stdin": {"ref": "#reads"},
    "stdout": "output.sam"
}
