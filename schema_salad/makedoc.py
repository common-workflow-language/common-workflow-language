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
import argparse

_logger = logging.getLogger("salad")

def has_types(items):
    r = []
    if isinstance(items, dict):
        if items["type"] == "https://w3id.org/cwl/salad#record":
            return [items["name"]]
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
        self.toc += """<li><a href="#%s">%s %s</a><ol>\n""" %(to_id(title),
            num, title)
        return num

    def contents(self, id):
        c = """<h1 id="%s">Table of contents</h1>
               <nav class="tocnav"><ol>%s""" % (id, self.toc)
        c += "</ol>"
        for i in range(0, len(self.numbering)):
            c += "</li></ol>"
        c += """</nav>"""
        return c

basicTypes = ("https://w3id.org/cwl/salad#null",
              "http://www.w3.org/2001/XMLSchema#boolean",
              "http://www.w3.org/2001/XMLSchema#int",
              "http://www.w3.org/2001/XMLSchema#long",
              "http://www.w3.org/2001/XMLSchema#float",
              "http://www.w3.org/2001/XMLSchema#double",
              "http://www.w3.org/2001/XMLSchema#string",
              "https://w3id.org/cwl/salad#record",
              "https://w3id.org/cwl/salad#enum",
              "https://w3id.org/cwl/salad#array")

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

def fix_doc(doc):
    if isinstance(doc, list):
        doc = "".join(doc)
    return "\n".join([re.sub(r"<([^>@]+@[^>]+)>", r"[\1](mailto:\1)", d) for d in doc.splitlines()])

class RenderType(object):
    def __init__(self, toc, j, renderlist, redirects):
        self.typedoc = StringIO.StringIO()
        self.toc = toc
        self.subs = {}
        self.docParent = {}
        self.docAfter = {}
        self.rendered = set()
        self.redirects = redirects
        self.title = None

        for t in j:
            if "extends" in t:
                for e in aslist(t["extends"]):
                    add_dictlist(self.subs, e, t["name"])
                    #if "docParent" not in t and "docAfter" not in t:
                    #    add_dictlist(self.docParent, e, t["name"])

            if t.get("docParent"):
                add_dictlist(self.docParent, t["docParent"], t["name"])

            if t.get("docChild"):
                for c in aslist(t["docChild"]):
                    add_dictlist(self.docParent, t["name"], c)

            if t.get("docAfter"):
                add_dictlist(self.docAfter, t["docAfter"], t["name"])

        _, _, metaschema_loader = schema.get_metaschema()
        alltypes = schema.extend_and_specialize(j, metaschema_loader)

        self.typemap = {}
        self.uses = {}
        self.record_refs = {}
        for t in alltypes:
            self.typemap[t["name"]] = t
            try:
                if t["type"] == "record":
                    self.record_refs[t["name"]] = []
                    for f in t.get("fields", []):
                        p = has_types(f)
                        for tp in p:
                            if tp not in self.uses:
                                self.uses[tp] = []
                            if (t["name"], f["name"]) not in self.uses[tp]:
                                _, frg1 = urlparse.urldefrag(t["name"])
                                _, frg2 = urlparse.urldefrag(f["name"])
                                self.uses[tp].append((frg1, frg2))
                            if tp not in basicTypes and tp not in self.record_refs[t["name"]]:
                                    self.record_refs[t["name"]].append(tp)
            except KeyError as e:
                _logger.error("Did not find 'type' in %s", t)
                raise

        for f in alltypes:
            if (f["name"] in renderlist or
                ((not renderlist) and
                 ("extends" not in f) and
                 ("docParent" not in f) and
                 ("docAfter" not in f))):
                self.render_type(f, 1)

    def typefmt(self, tp, redirects, nbsp=False):
        global primitiveType
        if isinstance(tp, list):
            if nbsp and len(tp) <= 3:
                return "&nbsp;|&nbsp;".join([self.typefmt(n, redirects) for n in tp])
            else:
                return " | ".join([self.typefmt(n, redirects) for n in tp])
        if isinstance(tp, dict):
            if tp["type"] == "https://w3id.org/cwl/salad#array":
                return "array&lt;%s&gt;" % (self.typefmt(tp["items"], redirects, nbsp=True))
            if tp["type"] in ("https://w3id.org/cwl/salad#record", "https://w3id.org/cwl/salad#enum"):
                frg = schema.avro_name(tp["name"])
                if tp["name"] in redirects:
                    return """<a href="%s">%s</a>""" % (redirects[tp["name"]], frg)
                elif tp["name"] in self.typemap:
                    return """<a href="#%s">%s</a>""" % (to_id(frg), frg)
                else:
                    return frg
            if isinstance(tp["type"], dict):
                return self.typefmt(tp["type"], redirects)
        else:
            if str(tp) in redirects:
                return """<a href="%s">%s</a>""" % (redirects[tp], redirects[tp])
            elif str(tp) in basicTypes:
                return """<a href="%s">%s</a>""" % (primitiveType, schema.avro_name(str(tp)))
            else:
                _, frg = urlparse.urldefrag(tp)
                if frg:
                    tp = frg
                return """<a href="#%s">%s</a>""" % (to_id(tp), tp)


    def render_type(self, f, depth):
        if f["name"] in self.rendered or f["name"] in self.redirects:
            return
        self.rendered.add(f["name"])

        if "doc" not in f:
            f["doc"] = ""

        f["type"] = copy.deepcopy(f)
        f["doc"] = ""
        f = f["type"]

        if "doc" not in f:
            f["doc"] = ""

        def extendsfrom(item, ex):
            if "extends" in item:
                for e in aslist(item["extends"]):
                    ex.insert(0, self.typemap[e])
                    extendsfrom(self.typemap[e], ex)

        ex = [f]
        extendsfrom(f, ex)

        enumDesc = {}
        if f["type"] == "enum" and isinstance(f["doc"], list):
            for e in ex:
                for i in e["doc"]:
                    idx = i.find(":")
                    if idx > -1:
                        enumDesc[i[:idx]] = i[idx+1:]
                e["doc"] = [i for i in e["doc"] if i.find(":") == -1 or i.find(" ") < i.find(":")]

        f["doc"] = fix_doc(f["doc"])

        if f["type"] == "record":
            for field in f.get("fields", []):
                if "doc" not in field:
                    field["doc"] = ""

        if f["type"] != "documentation":
            lines = []
            for l in f["doc"].splitlines():
                if len(l) > 0 and l[0] == "#":
                    l = ("#" * depth) + l
                lines.append(l)
            f["doc"] = "\n".join(lines)

            _, frg = urlparse.urldefrag(f["name"])
            num = self.toc.add_entry(depth, frg)
            doc = "## %s %s\n" % (num, frg)
        else:
            doc = ""

        if self.title is None:
            self.title = f["doc"][0:f["doc"].index("\n")][2:]

        if f["type"] == "documentation":
            f["doc"] = number_headings(self.toc, f["doc"])

        #if "extends" in f:
        #    doc += "\n\nExtends "
        #    doc += ", ".join([" %s" % linkto(ex) for ex in aslist(f["extends"])])
        #if f["name"] in self.subs:
        #    doc += "\n\nExtended by"
        #    doc += ", ".join([" %s" % linkto(s) for s in self.subs[f["name"]]])
        #if f["name"] in self.uses:
        #    doc += "\n\nReferenced by"
        #    doc += ", ".join([" [%s.%s](#%s)" % (s[0], s[1], to_id(s[0])) for s in self.uses[f["name"]]])

        doc = doc + "\n\n" + f["doc"]

        doc = mistune.markdown(doc, renderer=MyRenderer())

        if f["type"] == "record":
            doc += "<h3>Fields</h3>"
            doc += """<table class="table table-striped">"""
            doc += "<tr><th>field</th><th>type</th><th>required</th><th>description</th></tr>"
            required = []
            optional = []
            for i in f.get("fields", []):
                tp = i["type"]
                if isinstance(tp, list) and tp[0] == "https://w3id.org/cwl/salad#null":
                    opt = False
                    tp = tp[1:]
                else:
                    opt = True

                desc = i["doc"]
                #if "inherited_from" in i:
                #    desc = "%s _Inherited from %s_" % (desc, linkto(i["inherited_from"]))

                frg = schema.avro_name(i["name"])
                tr = "<td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td>" % (frg, self.typefmt(tp, self.redirects), opt, mistune.markdown(desc))
                if opt:
                    required.append(tr)
                else:
                    optional.append(tr)
            for i in required+optional:
                doc += "<tr>" + i + "</tr>"
            doc += """</table>"""
        elif f["type"] == "enum":
            doc += "<h3>Symbols</h3>"
            doc += """<table class="table table-striped">"""
            doc += "<tr><th>symbol</th><th>description</th></tr>"
            for e in ex:
                for i in e.get("symbols", []):
                    doc += "<tr>"
                    frg = schema.avro_name(i)
                    doc += "<td><code>%s</code></td><td>%s</td>" % (frg, enumDesc.get(frg, ""))
                    doc += "</tr>"
            doc += """</table>"""
        f["doc"] = doc

        self.typedoc.write(f["doc"])

        subs = self.docParent.get(f["name"], []) + self.record_refs.get(f["name"], [])
        if len(subs) == 1:
            self.render_type(self.typemap[subs[0]], depth)
        else:
            for s in subs:
                self.render_type(self.typemap[s], depth+1)

        for s in self.docAfter.get(f["name"], []):
            self.render_type(self.typemap[s], depth)

def avrold_doc(j, outdoc, renderlist, redirects, brand, brandlink):
    toc = ToC()
    toc.start_numbering = False

    rt = RenderType(toc, j, renderlist, redirects)
    content = rt.typedoc.getvalue()

    outdoc.write("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
    """)

    outdoc.write("<title>%s</title>" % (rt.title))

    outdoc.write("""
    <style>
    :target {
      padding-top: 61px;
      margin-top: -61px;
    }
    body {
      padding-top: 61px;
    }
    .tocnav ol {
      list-style: none
    }
    </style>
    </head>
    <body>
    """)

    outdoc.write("""
      <nav class="navbar navbar-default navbar-fixed-top">
        <div class="container">
          <div class="navbar-header">
            <a class="navbar-brand" href="%s">%s</a>
    """ % (brandlink, brand))

    if u"<!--ToC-->" in content:
        content = content.replace(u"<!--ToC-->", toc.contents("toc"))
        outdoc.write("""
                <ul class="nav navbar-nav">
                  <li><a href="#toc">Table of contents</a></li>
                </ul>
        """)

    outdoc.write("""
          </div>
        </div>
      </nav>
    """)

    outdoc.write("""
    <div class="container">
    """)

    outdoc.write("""
    <div class="row">
    """)

    outdoc.write("""
    <div class="col-md-12" role="main" id="main">""")

    outdoc.write(content.encode("utf-8"))

    outdoc.write("""</div>""")

    outdoc.write("""
    </div>
    </div>
    </body>
    </html>""")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("schema")
    parser.add_argument('--only', action='append')
    parser.add_argument('--redirect', action='append')
    parser.add_argument('--brand')
    parser.add_argument('--brandlink')
    parser.add_argument('--primtype', default="#PrimitiveType")

    args = parser.parse_args()

    s = []
    a = args.schema
    with open(a) as f:
        if a.endswith("md"):
            s.append({"name": os.path.splitext(os.path.basename(a))[0],
                  "type": "documentation",
                  "doc": f.read().decode("utf-8")
              })
        else:
            uri = "file://" + os.path.abspath(a)
            _, _, metaschema_loader = schema.get_metaschema()
            j, schema_metadata = metaschema_loader.resolve_ref(uri, "")
            if isinstance(j, list):
                s.extend(j)
            else:
                s.append(j)

    primitiveType = args.primtype

    redirect = {r.split("=")[0]:r.split("=")[1] for r in args.redirect} if args.redirect else {}
    renderlist = args.only if args.only else []
    avrold_doc(s, sys.stdout, renderlist, redirect, args.brand, args.brandlink)
