{
    "cwlVersion": "v1.0", 
    "$graph": [
        {
            "inputs": [
                {
                    "type": "string", 
                    "id": "#main/bam"
                }, 
                {
                    "type": "#capture_kit.yml/capture_kit", 
                    "id": "#main/capture_kit"
                }
            ], 
            "requirements": [
                {
                    "class": "SchemaDefRequirement", 
                    "types": [
                        {
                            "fields": [
                                {
                                    "type": "string", 
                                    "name": "#capture_kit.yml/capture_kit/bait"
                                }
                            ], 
                            "type": "record", 
                            "name": "#capture_kit.yml/capture_kit"
                        }
                    ]
                }
            ], 
            "outputs": [
                {
                    "outputSource": "#main/touch_bam/empty_file", 
                    "type": "File", 
                    "id": "#main/output_bam"
                }
            ], 
            "class": "Workflow", 
            "steps": [
                {
                    "out": [
                        "#main/touch_bam/empty_file"
                    ], 
                    "run": "#touch.cwl", 
                    "id": "#main/touch_bam", 
                    "in": [
                        {
                            "source": "#main/bam", 
                            "id": "#main/touch_bam/name"
                        }
                    ]
                }
            ], 
            "id": "#main"
        }, 
        {
            "inputs": [
                {
                    "inputBinding": {
                        "position": 0
                    }, 
                    "type": "string", 
                    "id": "#touch.cwl/name"
                }
            ], 
            "outputs": [
                {
                    "outputBinding": {
                        "glob": "$(inputs.name)"
                    }, 
                    "type": "File", 
                    "id": "#touch.cwl/empty_file"
                }
            ], 
            "baseCommand": [
                "touch"
            ], 
            "class": "CommandLineTool", 
            "id": "#touch.cwl", 
            "hints": [
                {
                    "dockerPull": "debian:stretch-slim", 
                    "class": "DockerRequirement"
                },
                {
                    "class": "ResourceRequirement",
                    "ramMin": 128
                }
            ]
        }
    ]
}
