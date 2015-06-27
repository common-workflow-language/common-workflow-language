import json
from rdflib import Graph, plugin
from rdflib.serializer import Serializer

def printrdf(workflow, wf, ctx, sr):
    wf["@context"] = ctx
    g = Graph().parse(data=json.dumps(wf), format='json-ld', location=workflow)
    print(g.serialize(format=sr))

def printdot(workflow, wf, ctx, sr):
    wf["@context"] = ctx
    g = Graph().parse(data=json.dumps(wf), format='json-ld', location=workflow)

    print "digraph {"

    #g.namespace_manager.qname(predicate)

    def lastpart(uri):
        uri = str(uri)
        if "/" in uri:
            return uri[uri.rindex("/")+1:]
        else:
            return uri

    qres = g.query(
        """SELECT ?step ?run
           WHERE {
              ?step cwl:run ?run .
           }""")

    for step, run in qres:
        print '"%s" [label="%s"]' % (lastpart(step), "%s (%s)" % (lastpart(step), lastpart(run)))

    qres = g.query(
        """SELECT ?step ?inp ?source
           WHERE {
              ?wf cwl:steps ?step .
              ?step cwl:inputs ?inp .
              ?inp cwl:source ?source .
           }""")

    for step, inp, source in qres:
        print '"%s" [shape=box]' % (lastpart(inp))
        print '"%s" -> "%s" [label="%s"]' % (lastpart(source), lastpart(inp), "")
        print '"%s" -> "%s" [label="%s"]' % (lastpart(inp), lastpart(step), "")

    qres = g.query(
        """SELECT ?step ?out
           WHERE {
              ?wf cwl:steps ?step .
              ?step cwl:outputs ?out .
           }""")

    for step, out in qres:
        print '"%s" [shape=box]' % (lastpart(out))
        print '"%s" -> "%s" [label="%s"]' % (lastpart(step), lastpart(out), "")

    qres = g.query(
        """SELECT ?out ?source
           WHERE {
              ?wf cwl:outputs ?out .
              ?out cwl:source ?source .
           }""")

    for out, source in qres:
        print '"%s" [shape=octagon]' % (lastpart(out))
        print '"%s" -> "%s" [label="%s"]' % (lastpart(source), lastpart(out), "")

    qres = g.query(
        """SELECT ?inp
           WHERE {
              ?wf rdf:type cwl:Workflow .
              ?wf cwl:inputs ?inp .
           }""")

    for (inp,) in qres:
        print '"%s" [shape=octagon]' % (lastpart(inp))


    print "}"
