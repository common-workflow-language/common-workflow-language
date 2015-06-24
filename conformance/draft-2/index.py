#!/usr/bin/env python

# Toy program to generate inverted index of word to line.
# Takes input text file on stdin and prints output index on stdout.

import sys

words = {}

mainfile = sys.argv[1]
indexfile = sys.argv[1] + ".idx"

main = open(mainfile)
index = open(indexfile, "w")

linenum = 0
for l in main:
    linenum += 1
    l = l.rstrip().lower().replace(".", "").replace(",", "").replace(";", "").replace("-", " ")
    for w in l.split(" "):
        if w:
            if w not in words:
                words[w] = set()
            words[w].add(linenum)

for w in sorted(words.keys()):
    index.write("%s: %s" % (w, ", ".join((str(i) for i in words[w]))) + "\n")
