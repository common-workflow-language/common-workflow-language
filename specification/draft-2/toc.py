#!/usr/bin/env python

import re

n1 = 0
n2 = 0

toc = ''

with open("workflow-description.md") as f:
    for line in f:
        if line.strip() not in ("# Abstract", "# Status of This Document", "# Table of Contents"):
            m = re.match(r'^#(#?) (.*)', line)
            if m:
                if m.group(1):
                    n2 += 1
                    toc += "  %i. [%s](#%s)\n" % (
                        n2,
                        m.group(2),
                        m.group(2).lower().replace(' ', '-'))
                else:
                    n1 += 1
                    n2 = 0
                    toc += "%i. [%s](#%s)\n" % (
                        n1,
                        m.group(2),
                        m.group(2).lower().replace(' ', '-'))

print toc
