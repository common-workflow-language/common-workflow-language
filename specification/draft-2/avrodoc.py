#!/usr/bin/env python

import cwltool.process
import shutil
import json
import yaml
import os
import subprocess
import copy

# Uses avrodoc https://github.com/ept/avrodoc
# npm install avrodoc -g

shutil.rmtree("out", True)
os.mkdir("out")

module_dir = os.path.dirname(os.path.abspath(__file__))
cwl_avsc = os.path.join(module_dir, '../../schemas/draft-2/cwl-avro.yml')
n = []

out = {"type": "record", "name": ""}

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
                for s in subs[f["name"]]:
                    f["doc"] += " [%s](#/schema/%s)" % (s, s)

fn = "out/in.avsc"
with open(fn, "w") as f:
    json.dump(out, f, indent=True)

with open("out/doc.html", "w") as f:
    subprocess.check_call(["avrodoc", "out/in.avsc"], stdout=f)
