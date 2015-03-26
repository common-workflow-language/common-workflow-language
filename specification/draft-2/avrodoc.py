#!/usr/bin/env python

import cwltool.process
import shutil
import json
import yaml
import os
import subprocess
import copy
import pprint
import re

# Uses avrodoc https://github.com/ept/avrodoc
# npm install avrodoc -g

shutil.rmtree("out", True)
os.mkdir("out")

module_dir = os.path.dirname(os.path.abspath(__file__))
cwl_avsc = os.path.join(module_dir, '../../schemas/draft-2/cwl-avro.yml')
n = []

with open("workflow-description.md") as md:
    maindoc = md.read()

n1 = 0
n2 = 0

toc = ''

mdlines = []
for line in maindoc.splitlines():
    if line.strip() not in ("# Abstract", "# Status of This Document", "# Table of Contents"):
        m = re.match(r'^#(#?) (.*)', line)
        if m:
            if m.group(1):
                n2 += 1
                toc += "  %i. %s\n" % (
                    n2,
                    m.group(2))
                line = "## %i.%i %s" % (n1, n2, m.group(2))
            else:
                n1 += 1
                n2 = 0
                toc += "%i. %s\n" % (
                    n1,
                    m.group(2))
                line = "# %i. %s" % (n1, m.group(2))
    line = re.sub(r'^(https?://\S+)', r'[\1](\1)', line)
    mdlines.append(line)

maindoc = '\n'.join(mdlines)

maindoc = maindoc.replace("# Table of Contents", "# Table of Contents\n\n%s" % toc)



out = {"type": "record", "name": " Common Workflow Language, Draft 2", "doc":maindoc}

with open(cwl_avsc) as f:
    j = yaml.load(f)
    subs = {}
    for t in j:
        if "extends" in t:
            if t["extends"] not in subs:
                subs[t["extends"]] = []
            subs[t["extends"]].append(t["name"])

    out["fields"] = cwltool.process.extend_avro(j)
    for f in out["fields"]:
        if "doc" not in f:
            f["doc"] = ""

        f["type"] = copy.deepcopy(f)
        f = f["type"]
        if "doc" not in f:
            f["doc"] = ""
        if f["type"] == "record":
            for field in f["fields"]:
                if "doc" not in field:
                    field["doc"] = ""
        if "extends" in f:
            f["doc"] += "Extends [%s](#/schema/%s)" % (f["extends"], f["extends"])
        if f["name"] in subs:
            f["doc"] += "\n\nExtended by"
            f["doc"] += ", ".join([" [%s](#/schema/%s)" % (s, s) for s in subs[f["name"]]])

fn = "out/in.avsc"
with open(fn, "w") as f:
    json.dump(out, f, indent=True)

with open("out/doc.html", "w") as f:
    subprocess.check_call(["avrodoc", "out/in.avsc"], stdout=f)
