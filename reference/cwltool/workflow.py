import os
import logging
import functools
import json
from datetime import datetime

from rdflib import Graph, URIRef, Literal, RDF, XSD
from rdflib.namespace import Namespace, NamespaceManager


log = logging.getLogger(__file__)

CWL = Namespace('http://github.com/common-workflow-language/schema/wf#')
PROV = Namespace('http://www.w3.org/ns/prov#')


class JsonLiteral(Literal):
    def __init__(self, val):
        super(JsonLiteral, self).__init__(json.dumps(val), datatype='http://json.org')


def lazy(func):
    attr = '__lazy_' + func.__name__

    @functools.wraps(func)
    def wrapped(self):
        if not hasattr(self, attr):
            setattr(self, attr, func(self))
        return getattr(self, attr)
    return property(wrapped)


class Activity(object):
    def __init__(self, graph, iri):
        self.g = graph
        self.iri = iri

    @lazy
    def process(self):
        return self.g.value(self.iri, CWL.activityFor)

    @lazy
    def inputs(self):
        return list(self.g.objects(self.process, CWL.inputs))

    @lazy
    def outputs(self):
        return list(self.g.objects(self.process, CWL.outputs))

    @lazy
    def has_prereqs(self):
        return all([None, CWL.producedByPort, src] in self.g for src in self.sources)

    @lazy
    def started(self):
        return self.g.value(self.iri, PROV.startedAtTime)

    @lazy
    def ended(self):
        return self.g.value(self.iri, PROV.endedAtTime)

    @lazy
    def sources(self):
        return [x[0] for x in self.g.query('''
        select ?src
        where {
            <%s> cwl:inputs ?port .
            ?x cwl:destination ?port .
            ?x cwl:source ?src .
        }
        ''' % self.process)]


class WorkflowRunner(object):
    def __init__(self):
        nm = NamespaceManager(Graph())
        nm.bind('cwl', CWL)
        nm.bind('prov', PROV)
        self.g = Graph(namespace_manager=nm)
        self.wf_iri = None
        self.act_iri = None

    def load(self, *args, **kwargs):
        return self.g.parse(*args, **kwargs)

    def iri_for_activity(self, process_iri):
        sep = '/' if '#' in process_iri else '#'
        return URIRef(process_iri + sep + 'activity')

    def iri_for_value(self, port_iri):
        return URIRef(port_iri + '/value')

    def get_ready(self):
        activities = [Activity(self.g, iri) for iri in self.g.subjects(RDF.type, CWL.Activity)]
        return [a for a in activities if a.has_prereqs and not a.started]

    def set_value(self, port_iri, value, creator_iri=None):
        if not port_iri.startswith(self.wf_iri):
            port_iri = self.wf_iri + '#' + port_iri
        iri = self.iri_for_value(port_iri)
        self.g.add([iri, RDF.value, JsonLiteral(value)])
        self.g.add([iri, CWL.producedByPort, URIRef(port_iri)])
        if creator_iri:
            self.g.add([iri, PROV.wasGeneratedBy, URIRef(creator_iri)])
        return iri

    @classmethod
    def from_workflow(cls, path):
        instance = cls()
        g = instance.g
        instance.load(path, format='json-ld')
        instance.wf_iri = URIRef('file://' + path)  # FIXME
        iri = instance.iri_for_activity(instance.wf_iri)
        instance.act_iri = iri
        g.add([iri, RDF.type, CWL.Activity])
        g.add([iri, CWL.activityFor, instance.wf_iri])
        g.add([iri, PROV.startedAtTime, Literal(datetime.now(), datatype=XSD.datetime)])
        for sp in g.objects(instance.wf_iri, CWL.steps):
            a = instance.iri_for_activity(sp)
            g.resource(a)
            g.add([a, RDF.type, CWL.Activity])
            g.add([a, CWL.activityFor, sp])
        return instance


def main():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../examples/wf_simple.json'))
    rnr = WorkflowRunner.from_workflow(path)

    def show_ready():
        for a in rnr.get_ready():
            print 'Ready to run:', a.iri

    base = rnr.wf_iri + '#'
    print 'Setting inputs...'
    rnr.set_value('a', 2)
    rnr.set_value('b', 3)
    show_ready()

    print 'Simulating sum...'
    rnr.g.add([base + 'sum/activity', PROV.startedAtTime, Literal(1)])
    rnr.set_value('sum/c', 6)
    rnr.g.add([base + 'sum/activity', PROV.endedAtTime, Literal(1)])
    show_ready()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()