#!/usr/bin/env python


import json


def main():
    with open('job.cwl.json') as inp, open('result.cwl.json', 'w') as out:
        job = json.load(inp)
        json.dump({
            'c': job['inputs']['a'] + job['inputs']['b']
        }, out)

if __name__ == '__main__':
    main()