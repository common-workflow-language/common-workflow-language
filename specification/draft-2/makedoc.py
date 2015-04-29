#!/usr/bin/env python

import mistune
import cwltool.process
import shutil
import json
import yaml
import os
import subprocess
import copy
import pprint
import re
import sys

module_dir = os.path.dirname(os.path.abspath(__file__))
cwl_avsc = sys.argv[1] # os.path.join(module_dir, '../../schemas/draft-2/cwl-avro.yml')

def has_types(items):
    r = []
    if isinstance(items, dict):
        for n in ("type", "items", "values"):
            if n in items:
                r.extend(has_types(items[n]))
        return r
    if isinstance(items, list):
        for i in items:
            r.extend(has_types(i))
        return r
    if isinstance(items, basestring):
        return [items]
    return []


# with open(cwl_avsc) as f:
#     j = yaml.load(f)
#     subs = {}
#     for t in j:
#         if "extends" in t:
#             if t["extends"] not in subs:
#                 subs[t["extends"]] = []
#             subs[t["extends"]].append(t["name"])

#     out["fields"] = cwltool.process.extend_avro(j)

#     uses = {}
#     for t in out["fields"]:
#         if t["type"] == "record":
#             for f in t["fields"]:
#                 p = has_types(f)
#                 for tp in p:
#                     if tp not in uses:
#                         uses[tp] = []
#                     if (t["name"], f["name"]) not in uses[tp]:
#                         uses[tp].append((t["name"], f["name"]))

#     for f in out["fields"]:
#         if "doc" not in f:
#             f["doc"] = ""

#         f["type"] = copy.deepcopy(f)
#         f["doc"] = ""
#         f = f["type"]
#         if "doc" not in f:
#             f["doc"] = ""
#         if f["type"] == "record":
#             for field in f["fields"]:
#                 if "doc" not in field:
#                     field["doc"] = ""
#         doc = ""
#         if "extends" in f:
#             doc += "\n\nExtends [%s](#/schema/%s)" % (f["extends"], f["extends"])
#         if f["name"] in subs:
#             doc += "\n\nExtended by"
#             doc += ", ".join([" [%s](#/schema/%s)" % (s, s) for s in subs[f["name"]]])
#         if f["name"] in uses:
#             doc += "\n\nReferenced by"
#             doc += ", ".join([" [%s.%s](#/schema/%s)" % (s[0], s[1], s[0]) for s in uses[f["name"]]])
#         f["doc"] = doc + "\n\n" + f["doc"]

outdoc = open("index.html", "w")

outdoc.write("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<script src="http://code.jquery.com/jquery-1.11.2.min.js"></script>
<script src="http://code.jquery.com/jquery-migrate-1.2.1.min.js"></script>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
<style>
body {
  position: relative;
  background-color: aliceblue;
}

#main {
 background-color: white;
}

.nav > li > a {
  padding-top: 2px;
  padding-bottom: 2px;
}

ol > li > ol {
  list-style-type: none;
}
ol > li > ol > li {
  padding-left: 1em;
}

</style>
</head>
<body data-spy="scroll" data-target="#toc">
<div class="container-fluid">
""")

with open(sys.argv[2]) as md:
    maindoc = md.read()

n1 = 0
n2 = 0

toc = ''

mdlines = []
n = []

def to_id(text):
    textid = text
    if text[0] in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
        try:
            textid = text[text.index(" ")+1:]
        except ValueError:
            pass
    textid = textid.lower().replace(" ", "_")
    return textid

start_numbering = False
for line in maindoc.splitlines():
    if line.strip() == "# Introduction":
        start_numbering = True
    if start_numbering:
        m = re.match(r'^#(#?) (.*)', line)
        if m:
            if m.group(1):
                if n2 == 0:
                    toc += """<ol class="nav nav-pills nav-stacked">"""
                n2 += 1
                toc += """<li><a href="#%s">%i.%i %s</a></li>\n""" % (to_id(m.group(2)), n1, n2, m.group(2))
                line = "## %i.%i %s" % (n1, n2, m.group(2))
            else:
                if n2 > 0:
                    toc += "</ol>"
                if n1 > 0:
                    toc += "</li>"
                n1 += 1
                n2 = 0
                toc += """<li><a href="#%s">%i. %s</a>\n""" % (to_id(m.group(2)), n1, m.group(2))
                line = "# %i. %s" % (n1, m.group(2))
    elif len(line) > 0 and line[0] == "#":
        toc += """<li><a href="#%s">%s</a></li>\n""" % (to_id(line[2:]), line[2:])
    line = re.sub(r'^(https?://\S+)', r'[\1](\1)', line)
    mdlines.append(line)
toc += "</li>"

print toc

maindoc = '\n'.join(mdlines)


outdoc.write("""
<div class="row">
<div class="col-md-3 affix" role="complementary">
<nav id="toc">
<ol class="nav nav-pills nav-stacked">
""")
outdoc.write(toc)
outdoc.write("""</ol>
</nav>
</div>
</div>
""")

class MyRenderer(mistune.Renderer):
    def header(self, text, level, raw=None):
        return """<h1 id="%s">%s</h1>""" % (to_id(text), text)

outdoc.write("""
<div class="col-md-9 col-md-offset-3" role="main" id="main">""")
outdoc.write(mistune.markdown(maindoc, renderer=MyRenderer()))
outdoc.write("""</div>""")

outdoc.write("""
</div>
</html>""")

outdoc.close()
