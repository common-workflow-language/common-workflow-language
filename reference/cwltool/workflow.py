import os
import logging
import functools
import json
from datetime import datetime
from copy import deepcopy
from collections import defaultdict

from rdflib import Graph, URIRef, Literal, RDF, XSD
from rdflib.namespace import Namespace, NamespaceManager

from tool_new import jseval


log = logging.getLogger(__file__)

CWL = Namespace('http://github.com/common-workflow-language/')
PROV = Namespace('http://www.w3.org/ns/prov#')
DCT = Namespace('http://purl.org/dc/terms/')
CNT = Namespace('http://www.w3.org/2011/content#')


def get_value(graph, iri):
    chars = graph.value(iri, CNT.chars)
    if chars:
        return json.load(chars.toPython())
    return graph.value(iri).toPython()


def set_value(graph, iri, val):
    # TODO: add CWL.includesFile
    if isinstance(val, (dict, list)):
        graph.add(iri, CNT.chars, json.dumps(val))
    else:
        graph.add(iri, RDF.value, Literal(val))


class Inputs(object):
    def __init__(self, graph, tuples):
        self.g = graph
        self.d = {}
        self.wrapped = []
        for k, v in tuples:
            self[k] = v

    def __getitem__(self, item):
        return self.d[item]

    def __setitem__(self, key, value):
        if key not in self.d:
            self.d[key] = get_value(self.g, value)
        elif key in self.wrapped:
            self.d[key].append(get_value(self.g, value))
        else:
            self.d[key] = [self.d[key], get_value(self.g, value)]
            self.wrapped.append(key)

    def to_dict(self):
        return {k[k.rfind('/') + 1:]: v for k, v in self.d.iteritems()}


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

    activity = lazy(lambda self: self.g.value(None, CWL.activityFor, self.iri))
    inputs = lazy(lambda self: list(self.g.objects(self.iri, CWL.inputs)))
    outputs = lazy(lambda self: list(self.g.objects(self.iri, CWL.outputs)))
    started = lazy(lambda self: self.g.value(self.activity, PROV.startedAtTime) if self.activity else None)
    ended = lazy(lambda self: self.g.value(self.activity, PROV.endedAtTime) if self.activity else None)
    has_prereqs = lazy(lambda self: all([None, CWL.producedByPort, src] in self.g for src in self.sources))

    @lazy
    def has_prereqs(self):
        return all([None, CWL.producedByPort, src] in self.g for src in self.sources)

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
        return self.g.query('''
        select ?port ?val
        where {
            <%s> cwl:inputs ?port .
            ?link   cwl:destination ?port ;
                    cwl:source ?src .
            ?val cwl:producedByPort ?src .
        }
        ''' % self.iri)


class WorkflowRunner(object):
    def __init__(self, path):
        nm = NamespaceManager(Graph())
        nm.bind('cwl', CWL)
        nm.bind('prov', PROV)
        nm.bind('dct', DCT)
        nm.bind('cnt', CNT)
        self.g = Graph(namespace_manager=nm)
        self.wf_iri = None
        self.act_iri = None
        self._load(path)

    def _load(self, path):
        self.g.parse(path)
        self.wf_iri = URIRef('file://' + path)  # TODO: Find a better way to do this
        self.g.add([self.wf_iri, RDF.type, CWL.Process])
        for sp in self.g.objects(self.wf_iri, CWL.steps):
            self.g.add([sp, RDF.type, CWL.Process])
            tool = self.g.value(sp, CWL.tool)
            log.debug('Loading reference %s', tool)
            self.g.parse(tool, format='json-ld')

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
            self.g.add([self.act_iri, DCT.hasPart, iri])
            for k, v in Process(self.g, proc_iri).input_values:
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
        set_value(self.g, iri, value)
        self.g.add([iri, RDF.type, CWL.Value])
        self.g.add([iri, CWL.producedByPort, URIRef(port_iri)])
        if creator_iri:
            self.g.add([iri, PROV.wasGeneratedBy, URIRef(creator_iri)])
        return iri

    def _depth_mismatch_port(self, proc, inputs):
        depth_of = lambda x: 1 if isinstance(x, list) else 0  # TODO: fixme
        incoming = {k: depth_of(v) for k, v in inputs.d.iteritems()}
        expected = {k: self.g.value(k, CWL.depth).toPython() for k in proc.inputs}
        result = None
        for k, v in incoming.iteritems():
            if expected[k] != v:
                if result:
                    log.error('\nIncoming: %s\nExpected: %s', incoming, expected)
                    raise Exception('More than one port has mismatching depth.')
                if incoming[k] < expected[k]:
                    raise Exception('depth(incoming) < depth(expected); Wrapping must be done explicitly.')
                if incoming[k] - expected[k] > 1:
                    raise NotImplementedError('Only handling one nesting level at the moment.')
                result = k
        return result

    def run_component(self, tool, job):
        cmp_type = self.g.value(tool, RDF.type)
        if cmp_type == CWL.SimpleTransformTool:
            return self.run_script(tool, job)
        raise Exception('Unrecognized component type: %s' % cmp_type)

    def run_workflow(self):
        self.start()
        while self.queued():
            act = self.start(self.queued()[0].iri)
            proc = Process(self.g, self.g.value(act, CWL.activityFor))
            tool = self.g.value(proc.iri, CWL.tool)
            inputs = Inputs(self.g, proc.input_values)  # TODO: propagate desc<->impl
            dmp = self._depth_mismatch_port(proc, inputs)
            if not dmp:
                job = {'inputs': inputs.to_dict()}
                outputs = self.run_component(tool, job)
            else:
                jobs, outputs = [], defaultdict(list)
                for i in inputs[dmp]:
                    inp_copy = deepcopy(inputs)
                    inp_copy.d[dmp] = i
                    jobs.append({'inputs': inp_copy.to_dict()})
                for job in jobs:
                    outs = self.run_component(tool, job)
                    for k, v in outs.iteritems():
                        outputs[k].append(v)
            for k, v in outputs.iteritems():
                self.set_value(proc.iri + '/' + k, v, act)
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
        return {k: get_value(self.g, v) for k, v in outputs.iteritems()}

    def run_script(self, tool, job):
        expr = self.g.value(self.g.value(tool, CWL.script)).toPython()
        log.debug('Running expr %s\nJob: %s', expr, job)
        result = jseval(job, expr)
        logging.debug('Result: %s', result)
        return result


def aplusbtimesc(wf_name, a, b, c):
    print '\n\n--- %s ---\n\n' % wf_name
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../examples/' + wf_name))
    rnr = WorkflowRunner(path)
    rnr.set_value('a', a)
    rnr.set_value('b', b)
    rnr.set_value('c', c)
    outs = rnr.run_workflow()
    assert outs
    print '\nDone. Workflow outputs:'
    for k, v in outs.iteritems():
        print k, v
        assert v == (a+b)*c
    return rnr

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    aplusbtimesc('wf_simple.json', 2, 3, 4)
    aplusbtimesc('wf_lists.json', 2, 3, 4)
    aplusbtimesc('wf_map.json', 2, 3, 4)