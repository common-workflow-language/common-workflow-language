import os
import logging
import functools
import json
from datetime import datetime

from rdflib import Graph, URIRef, Literal, RDF, XSD
from rdflib.namespace import Namespace, NamespaceManager

from tool import jseval

log = logging.getLogger(__file__)

CWL = Namespace('http://github.com/common-workflow-language/schema/wf#')
PROV = Namespace('http://www.w3.org/ns/prov#')
DCTERMS = Namespace('http://purl.org/dc/terms/')


def lazy(func):
    attr = '__lazy_' + func.__name__

    @functools.wraps(func)
    def wrapped(self):
        if not hasattr(self, attr):
            setattr(self, attr, func(self))
        return getattr(self, attr)
    return property(wrapped)


class Process(object):
    def __init__(self, graph, iri):
        self.g = graph
        self.iri = URIRef(iri)

    @lazy
    def activity(self):
        return self.g.value(None, CWL.activityFor, self.iri)

    @lazy
    def inputs(self):
        return list(self.g.objects(self.iri, CWL.inputs))

    @lazy
    def outputs(self):
        return list(self.g.objects(self.iri, CWL.outputs))

    @lazy
    def has_prereqs(self):
        return all([None, CWL.producedByPort, src] in self.g for src in self.sources)

    @lazy
    def started(self):
        return self.g.value(self.activity, PROV.startedAtTime) if self.activity else None

    @lazy
    def ended(self):
        return self.g.value(self.activity, PROV.endedAtTime) if self.activity else None

    @lazy
    def sources(self):
        return [x[0] for x in self.g.query('''
        select ?src
        where {
            <%s> cwl:inputs ?port .
            ?link   cwl:destination ?port ;
                    cwl:source ?src .
        }
        ''' % self.iri)]

    @lazy
    def input_values(self):
        return dict(self.g.query('''
        select ?port ?val
        where {
            <%s> cwl:inputs ?port .
            ?link   cwl:destination ?port ;
                    cwl:source ?src .
            ?val cwl:producedByPort ?src .
        }
        ''' % self.iri))


class WorkflowRunner(object):
    def __init__(self):
        nm = NamespaceManager(Graph())
        nm.bind('cwl', CWL)
        nm.bind('prov', PROV)
        nm.bind('dcterms', DCTERMS)
        self.g = Graph(namespace_manager=nm)
        self.wf_iri = None
        self.act_iri = None

    def load(self, *args, **kwargs):
        return self.g.parse(*args, **kwargs)

    def start(self, proc_iri=None):
        main_act = False
        if not proc_iri:
            proc_iri = self.wf_iri
            main_act = True
        proc_iri = URIRef(proc_iri)
        iri = self.iri_for_activity(proc_iri)
        log.debug('Starting %s', iri)
        self.g.add([iri, RDF.type, CWL.Activity])
        self.g.add([iri, CWL.activityFor, proc_iri])
        self.g.add([iri, PROV.startedAtTime, Literal(datetime.now(), datatype=XSD.datetime)])
        if main_act:
            self.act_iri = iri
        else:
            self.g.add([self.act_iri, DCTERMS.hasPart, iri])
            for k, v in Process(self.g, proc_iri).input_values.iteritems():
                val = self.g.value(v)
                log.debug('Value on %s is %s', k, val.toPython())
        return iri

    def end(self, act_iri):
        act_iri = URIRef(act_iri)
        self.g.add([act_iri, PROV.endedAtTime, Literal(datetime.now(), datatype=XSD.datetime)])

    def iri_for_activity(self, process_iri):
        sep = '/' if '#' in process_iri else '#'
        return URIRef(process_iri + sep + '__activity__')  # TODO: Better IRIs

    def iri_for_value(self, port_iri):
        return URIRef(port_iri + '/__value__')  # TODO: Better IRIs

    def queued(self):
        ps = [Process(self.g, iri) for iri in self.g.subjects(RDF.type, CWL.Process)]
        return [p for p in ps if p.has_prereqs and not p.started]

    def set_value(self, port_iri, value, creator_iri=None):
        if not port_iri.startswith(self.wf_iri):
            port_iri = self.wf_iri + '#' + port_iri
        port_iri = URIRef(port_iri)
        iri = self.iri_for_value(port_iri)
        self.g.add([iri, RDF.type, CWL.Value])
        self.g.add([iri, RDF.value, Literal(value)])  # TODO: complex types as cnt; add CWL.includesFile
        self.g.add([iri, CWL.producedByPort, URIRef(port_iri)])
        if creator_iri:
            self.g.add([iri, PROV.wasGeneratedBy, URIRef(creator_iri)])
        return iri

    def run_workflow(self):
        self.start()
        while self.queued():
            act = self.start(self.queued()[0].iri)
            proc = self.g.value(act, CWL.activityFor)
            # TODO: self.g.add [act, PROV.used, value]
            outputs = self.run_script(proc)
            for k, v in outputs.iteritems():
                self.set_value(proc + '/' + k, v, act)
            self.end(act)
        self.end(self.act_iri)
        outputs = dict(self.g.query('''
        select ?port ?val
        where {
            <%s> cwl:outputs ?port .
            ?link   cwl:destination ?port ;
                    cwl:source ?src .
            ?val cwl:producedByPort ?src .
        }
        ''' % self.wf_iri))
        return {k: self.g.value(v) for k, v in outputs.iteritems()}

    def run_script(self, proc):
        proc = Process(self.g, proc)
        inputs = {k[k.rfind('/') + 1:]: self.g.value(v).toPython() for k, v in proc.input_values.iteritems()}
        job = {'inputs': inputs}
        tool = self.g.value(proc.iri, CWL.tool)
        expr = self.g.value(tool, CWL.expr)
        log.debug('Running expr %s\nJob: %s', expr, job)
        result = jseval(job, expr)
        logging.debug('Result: %s', result)
        return result

    @classmethod
    def from_workflow(cls, path):
        wfr = cls()
        wfr.load(path, format='json-ld')
        wfr.wf_iri = URIRef('file://' + path)  # TODO: Find a better way to do this
        wfr.g.add([wfr.wf_iri, RDF.type, CWL.Process])
        for sp in wfr.g.objects(wfr.wf_iri, CWL.steps):
            wfr.g.add([sp, RDF.type, CWL.Process])
            tool = wfr.g.value(sp, CWL.tool)
            log.debug('Loading reference %s', tool)
            wfr.g.parse(tool, format='json-ld')
        return wfr


def main():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../examples/wf_simple.json'))
    rnr = WorkflowRunner.from_workflow(path)
    rnr.set_value('a', 2)
    rnr.set_value('b', 3)
    outs = rnr.run_workflow()
    print '\nDone. Workflow outputs:'
    for k, v in outs.iteritems():
        print k, v

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()