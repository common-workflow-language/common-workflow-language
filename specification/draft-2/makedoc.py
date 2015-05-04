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

class MyRenderer(mistune.Renderer):
    def header(self, text, level, raw=None):
        return """<h1 id="%s">%s</h1>""" % (to_id(text), text)

def to_id(text):
    textid = text
    if text[0] in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
        try:
            textid = text[text.index(" ")+1:]
        except ValueError:
            pass
    textid = textid.lower().replace(" ", "_")
    return textid

class ToC(object):
    def __init__(self):
        self.first_toc_entry = True
        self.numbering = [0]
        self.toc = ""

    def add_entry(self, thisdepth, title):
        depth = len(self.numbering)
        if thisdepth < depth:
            self.toc += "</ol>"
            for n in range(0, depth-thisdepth):
                self.numbering.pop()
                self.toc += "</li></ol>"
            self.numbering[-1] += 1
        elif thisdepth == depth:
            if not self.first_toc_entry:
                self.toc += "</ol>"
            else:
                self.first_toc_entry = False
            self.numbering[-1] += 1
        elif thisdepth > depth:
            self.numbering.append(1)

        if start_numbering:
            num = "%i.%s" % (self.numbering[0], ".".join([str(n) for n in self.numbering[1:]]))
        else:
            num = ""
        self.toc += """<li><a href="#%s">%s %s</a><ol class="nav nav-pills nav-stacked nav-secondary">\n""" %(to_id(title),
            num, title)
        return num

    def contents(self, id):
        c = """<nav id="%s"><ol class="nav nav-pills nav-stacked">%s""" % (id, self.toc)
        c += "</ol>"
        for i in range(0, len(self.numbering)):
            c += "</li></ol>"
        c += """</nav>"""
        return c

def typefmt(tp, nbsp=False):
    if isinstance(tp, list):
        if nbsp:
            return "&nbsp;|&nbsp;".join([typefmt(n) for n in tp])
        else:
            return " | ".join([typefmt(n) for n in tp])
    if isinstance(tp, dict):
        if tp["type"] == "array":
            return "array&lt;%s&gt;" % (typefmt(tp["items"], True))
    else:
        if str(tp) in ("null", "boolean", "int", "long", "float", "double", "bytes", "string", "record", "enum", "array", "map"):
            return """<a href="#datatype">%s</a>""" % str(tp)
        else:
            return """<a href="#%s">%s</a>""" % (to_id(str(tp)), str(tp))

mdlines = []

with open(sys.argv[2]) as md:
    maindoc = md.read()

start_numbering = False

toc = ToC()

for line in maindoc.splitlines():
    if line.strip() == "# Introduction":
        start_numbering = True
        toc.numbering = [0]

    m = re.match(r'^(#+) (.*)', line)
    if m:
        num = toc.add_entry(len(m.group(1)), m.group(2))
        line = "%s %s %s" % (m.group(1), num, m.group(2))
    #elif len(line) > 0 and line[0] == "#":
    #    toc += """<li><a href="#%s">%s</a></li>\n""" % (to_id(line[2:]), line[2:])
    line = re.sub(r'^(https?://\S+)', r'[\1](\1)', line)
    mdlines.append(line)

maindoc = '\n'.join(mdlines)

with open(cwl_avsc) as f:
    j = yaml.load(f)

subs = {}
showUnder = {}

def add_dictlist(di, key, val):
    if key not in di:
        di[key] = []
    di[key].append(val)

for t in j:
    if "extends" in t:
        add_dictlist(subs, t["extends"], t["name"])
        if "showUnder" not in t:
            add_dictlist(showUnder, t["extends"], t["name"])

    if t.get("showUnder"):
        add_dictlist(showUnder, t["showUnder"], t["name"])

alltypes = cwltool.process.extend_avro(j)

typemap = {}
uses = {}
for t in alltypes:
    typemap[t["name"]] = t
    if t["type"] == "record":
        for f in t["fields"]:
            p = has_types(f)
            for tp in p:
                if tp not in uses:
                    uses[tp] = []
                if (t["name"], f["name"]) not in uses[tp]:
                    uses[tp].append((t["name"], f["name"]))

class RenderType(object):
    def __init__(self):
        self.typedoc = ""

    def render_type(self, f, depth):
        if "doc" not in f:
            f["doc"] = ""

        f["type"] = copy.deepcopy(f)
        f["doc"] = ""
        f = f["type"]

        if "doc" not in f:
            f["doc"] = ""
        if f["type"] == "record":
            for field in f["fields"]:
                if "doc" not in field:
                    field["doc"] = ""

        lines = []
        for l in f["doc"].splitlines():
            if len(l) > 0 and l[0] == "#":
                l = "#" + l
            lines.append(l)
        f["doc"] = "\n".join(lines)

        num = toc.add_entry(depth, f["name"])
        doc = "## %s %s\n" % (num, f["name"])

        if "extends" in f:
            doc += "\n\nExtends [%s](#%s)" % (f["extends"], to_id(f["extends"]))
        if f["name"] in subs:
            doc += "\n\nExtended by"
            doc += ", ".join([" [%s](#%s)" % (s, to_id(s)) for s in subs[f["name"]]])
        if f["name"] in uses:
            doc += "\n\nReferenced by"
            doc += ", ".join([" [%s.%s](#%s)" % (s[0], s[1], to_id(s[0])) for s in uses[f["name"]]])
        doc = doc + "\n\n" + f["doc"]

        doc = mistune.markdown(doc, renderer=MyRenderer())

        if f["type"] == "record": # and not f.get("abstract"):
            doc += "<h3>Fields</h3>"
            doc += """<table class="table table-striped">"""
            doc += "<tr><th>field</th><th>type</th><th>required</th><th>description</th></tr>"
            for i in f["fields"]:
                doc += "<tr>"
                tp = i["type"]
                if isinstance(tp, list) and tp[0] == "null":
                    opt = False
                    tp = tp[1:]
                else:
                    opt = True
                doc += "<td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td>" % (i["name"], typefmt(tp), opt, mistune.markdown(i["doc"]))
                doc += "</tr>"
            doc += """</table>"""
        f["doc"] = doc

        self.typedoc += f["doc"]

        for s in showUnder.get(f["name"], []):
            self.render_type(typemap[s], depth+1)

rt = RenderType()
for f in alltypes:
    if "extends" not in f and not f.get("showUnder"):
        rt.render_type(f, 1)

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
html {
  height:100%;
}

body {
  height:100%;
  position: relative;
  background-color: aliceblue;
}

#main {
 background-color: white;
}

.nav > li > a {
  padding: 0px;
}

ol > li > ol {
  list-style-type: none;
}
ol > li > ol > li {
  padding-left: 1em;
}

.nav-secondary > li.active > a, .nav-pills > li.active > a:focus, .nav-pills > li.active > a:hover {
  text-decoration: underline;
  color: #337AB7;
  background-color: transparent;
}

.container-fluid {
  height: 100%;
}

.lefttoc {
  height: 100%;
  overflow-y: auto;
}

</style>
</head>
<body data-spy="scroll" data-target="#toc">
<div class="container-fluid">
""")

outdoc.write("""
<div class="row">
<div class="col-md-3 affix lefttoc" role="complementary">
""")
outdoc.write(toc.contents("toc"))
outdoc.write("""
</div>
</div>
""")


outdoc.write("""
<div class="col-md-9 col-md-offset-3" role="main" id="main">""")
outdoc.write(mistune.markdown(maindoc, renderer=MyRenderer()))

outdoc.write(rt.typedoc)

outdoc.write("""</div>""")

outdoc.write("""
</div>
</html>""")

outdoc.close()
