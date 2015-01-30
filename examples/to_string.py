#!/usr/bin/env python


import json


def main():
    with open('job.cwl.json') as inp, open('result.cwl.json', 'w') as out:
        job = json.load(inp)
        with open(job['inputs']['file1']['path']) as fp:
            contents = fp.read()
        json.dump({
            'result': contents
        }, out)

if __name__ == '__main__':
    main()