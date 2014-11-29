#!/usr/bin/env python

import json
import yaml
import glob
import os
import sys


if __name__ == '__main__':
    path = '.' if len(sys.argv) < 2 else sys.argv[1]
    for f in glob.glob(os.path.join(path, '*.yaml')):
        with open(f) as src, open(f + '.json', 'w') as dst:
            json.dump(yaml.load(src), dst, indent=2, sort_keys=True)
