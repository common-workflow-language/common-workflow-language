{
    "reads": {
        "class": "File",
        "location": "reads.fastq"
    },
    "stages": [
        {
            "algos": [
                {
                    "algo": "map1",
                    "minSeqLen": 20
                },
                {
                    "algo": "map2",
                    "minSeqLen": 20
                }
            ],
            "stageId": 1
        },
        {
            "algos": [
                {
                    "minSeqLen": 10,
                    "maxSeqLen": 20,
                    "seedLength": 16,
                    "algo": "map1"
                },
                {
                    "maxSeedHits": -1,
                    "minSeqLen": 10,
                    "maxSeqLen": 20,
                    "algo": "map2"
                }
            ],
            "stageId": 2
        }
    ]
}
