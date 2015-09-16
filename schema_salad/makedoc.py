import mistune
import schema
import json
import yaml
import os
import copy
import re
import sys
import StringIO
import logging
import urlparse
from aslist import aslist
import re

_logger = logging.getLogger("salad")

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

def linkto(item):
    _, frg = urlparse.urldefrag(item)
    return "[%s](#%s)" % (frg, to_id(frg))

class MyRenderer(mistune.Renderer):
    def header(self, text, level, raw=None):
        return """<h%i id="%s">%s</h1>""" % (level, to_id(text), text)

def to_id(text):
    textid = text
    if text[0] in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
        try:
            textid = text[text.index(" ")+1:]
        except ValueError:
            pass
    textid = textid.replace(" ", "_")
    return textid

class ToC(object):
    def __init__(self):
        self.first_toc_entry = True
        self.numbering = [0]
        self.toc = ""
        self.start_numbering = True

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

        if self.start_numbering:
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
        if nbsp and len(tp) <= 3:
            return "&nbsp;|&nbsp;".join([typefmt(n) for n in tp])
        else:
            return " | ".join([typefmt(n) for n in tp])
    if isinstance(tp, dict):
        if tp["type"] == "https://w3id.org/cwl/salad#array":
            return "array&lt;%s&gt;" % (typefmt(tp["items"], True))
        if tp["type"] in ("https://w3id.org/cwl/salad#record", "https://w3id.org/cwl/salad#enum"):
            frg = schema.avro_name(tp["name"])
            return """<a href="#%s">%s</a>""" % (to_id(frg), frg)
        if isinstance(tp["type"], dict):
            return typefmt(tp["type"])
    else:
        if str(tp) in ("https://w3id.org/cwl/salad#null",
                       "http://www.w3.org/2001/XMLSchema#boolean",
                       "http://www.w3.org/2001/XMLSchema#int",
                       "http://www.w3.org/2001/XMLSchema#long",
                       "http://www.w3.org/2001/XMLSchema#float",
                       "http://www.w3.org/2001/XMLSchema#double",
                       "http://www.w3.org/2001/XMLSchema#string",
                       "https://w3id.org/cwl/salad#record",
                       "https://w3id.org/cwl/salad#enum",
                       "https://w3id.org/cwl/salad#array"):
            return """<a href="#CWLType">%s</a>""" % schema.avro_name(str(tp))
        else:
            _, frg = urlparse.urldefrag(tp)
            if frg:
                tp = frg
            return """<a href="#%s">%s</a>""" % (to_id(tp), tp)

def add_dictlist(di, key, val):
    if key not in di:
        di[key] = []
    di[key].append(val)

def number_headings(toc, maindoc):
    mdlines = []
    skip = False
    for line in maindoc.splitlines():
        if line.strip() == "# Introduction":
            toc.start_numbering = True
            toc.numbering = [0]

        if line == "```":
            skip = not skip

        if not skip:
            m = re.match(r'^(#+) (.*)', line)
            if m:
                num = toc.add_entry(len(m.group(1)), m.group(2))
                line = "%s %s %s" % (m.group(1), num, m.group(2))
            line = re.sub(r'^(https?://\S+)', r'[\1](\1)', line)
        mdlines.append(line)

    maindoc = '\n'.join(mdlines)
    return maindoc

def fix_emails(doc):
    return "\n".join([re.sub(r"<([^>@]+@[^>]+)>", r"[\1](mailto:\1)", d) for d in doc.splitlines()])

class RenderType(object):
    def __init__(self, toc, j):
        self.typedoc = StringIO.StringIO()
        self.toc = toc
        self.subs = {}
        self.docParent = {}
        self.docAfter = {}
        for t in j:
            if "extends" in t:
                for e in aslist(t["extends"]):
                    add_dictlist(self.subs, e, t["name"])
                    if "docParent" not in t and "docAfter" not in t:
                        add_dictlist(self.docParent, e, t["name"])

            if t.get("docParent"):
                add_dictlist(self.docParent, t["docParent"], t["name"])

            if t.get("docAfter"):
                add_dictlist(self.docAfter, t["docAfter"], t["name"])

        _, _, metaschema_loader = schema.get_metaschema()
        alltypes = schema.extend_and_specialize(j, metaschema_loader)

        self.typemap = {}
        self.uses = {}
        for t in alltypes:
            self.typemap[t["name"]] = t
            if t["type"] == "https://w3id.org/cwl/salad#record":
                for f in t["fields"]:
                    p = has_types(f)
                    for tp in p:
                        if tp not in self.uses:
                            self.uses[tp] = []
                        if (t["name"], f["name"]) not in self.uses[tp]:
                            _, frg1 = urlparse.urldefrag(t["name"])
                            _, frg2 = urlparse.urldefrag(f["name"])
                            self.uses[tp].append((frg1, frg2))

        for f in alltypes:
            if ("extends" not in f) and ("docParent" not in f) and ("docAfter" not in f):
                self.render_type(f, 1)


    def render_type(self, f, depth):
        if "doc" not in f:
            f["doc"] = ""

        f["type"] = copy.deepcopy(f)
        f["doc"] = ""
        f = f["type"]

        if "doc" not in f:
            f["doc"] = ""

        f["doc"] = fix_emails(f["doc"])

        if f["type"] == "record":
            for field in f["fields"]:
                if "doc" not in field:
                    field["doc"] = ""

        if f["type"] != "documentation":
            lines = []
            for l in f["doc"].splitlines():
                if len(l) > 0 and l[0] == "#":
                    l = "#" + l
                lines.append(l)
            f["doc"] = "\n".join(lines)

            _, frg = urlparse.urldefrag(f["name"])
            num = self.toc.add_entry(depth, frg)
            doc = "## %s %s\n" % (num, frg)
        else:
            doc = ""

        if f["type"] == "documentation":
            f["doc"] = number_headings(self.toc, f["doc"])

        if "extends" in f:
            doc += "\n\nExtends "
            doc += ", ".join([" %s" % linkto(ex) for ex in aslist(f["extends"])])
        if f["name"] in self.subs:
            doc += "\n\nExtended by"
            doc += ", ".join([" %s" % linkto(s) for s in self.subs[f["name"]]])

        if f["name"] in self.uses:
            doc += "\n\nReferenced by"
            doc += ", ".join([" [%s.%s](#%s)" % (s[0], s[1], to_id(s[0])) for s in self.uses[f["name"]]])
        doc = doc + "\n\n" + f["doc"]

        doc = mistune.markdown(doc, renderer=MyRenderer())

        if f["type"] == "record":
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

                desc = i["doc"]
                if "inherited_from" in i:
                    desc = "%s _Inherited from %s_" % (desc, linkto(i["inherited_from"]))

                frg = schema.avro_name(i["name"])
                doc += "<td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td>" % (frg, typefmt(tp), opt, mistune.markdown(desc))
                doc += "</tr>"
            doc += """</table>"""
        f["doc"] = doc

        self.typedoc.write(f["doc"])

        for s in self.docParent.get(f["name"], []):
            self.render_type(self.typemap[s], depth+1)

        for s in self.docAfter.get(f["name"], []):
            self.render_type(self.typemap[s], depth)

def avrold_doc(j, outdoc):
    toc = ToC()
    toc.start_numbering = False

    rt = RenderType(toc, j)

    outdoc.write("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <script src="http://code.jquery.com/jquery-1.11.2.min.js"></script>
    <script src="http://code.jquery.com/jquery-migrate-1.2.1.min.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
    """)

    outdoc.write("<title>%s</title>" % (j[0]["name"]))

    outdoc.write("""
    <style>
    html {
      height:100%;
    }

    body {
      height:100%;
      position: relative;
    }

    #main {
     background-color: white;
    }

    .nav > li > a {
      padding: 0px;
    }

    ol {
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

    #main {
      overflow-y: auto;
    }

    #lefttoc {
      background-color: aliceblue;
      overflow-y: auto;
    }

    #toc {
      margin-top: 1em;
      margin-bottom: 2em;
    }

    @media (min-width: 992px) {
      .full-height {
        height: 100%;
      }
      #lefttoc {
        border-right: thin solid #C0C0C0;
      }
    }

    </style>
    </head>
    <body>
    <div class="container-fluid full-height">
    """)

    outdoc.write("""
    <div class="row full-height">
    <div id="lefttoc" class="col-md-3 full-height" role="complementary">
    """)
    outdoc.write(toc.contents("toc"))
    outdoc.write("""
    </div>
    """)

    outdoc.write("""
    <div class="col-md-9 full-height" role="main" id="main" data-spy="scroll" data-target="#toc">""")

    outdoc.write(rt.typedoc.getvalue().encode("utf-8"))

    outdoc.write("""</div>""")

    outdoc.write("""
    </div>
    </div>
    </body>
    </html>""")

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        if sys.argv[1].endswith("yml") or sys.argv[1].endswith("yaml"):
            uri = "file://" + os.path.abspath(sys.argv[1])
            _, _, metaschema_loader = schema.get_metaschema()
            j, schema_metadata = metaschema_loader.resolve_ref(uri, "")
        else:
            j = [{"name": sys.argv[2],
                  "type": "documentation",
                  "doc": f.read().decode("utf-8")
              }]
        avrold_doc(j, sys.stdout)
