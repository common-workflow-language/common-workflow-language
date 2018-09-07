#!/usr/bin/env python

# Toy program to search inverted index and print out each line the term
# appears.

from __future__ import print_function

import sys

mainfile = sys.argv[1]
indexfile = sys.argv[1] + ".idx1"
term = sys.argv[2]

main = open(mainfile)
index = open(indexfile)

st = term + ": "

for a in index:
    if a.startswith(st):
        n = [int(i) for i in a[len(st):].split(", ") if i]
        linenum = 0
        for l in main:
            linenum += 1
            if linenum in n:
                print(linenum, l.rstrip())
        break
