#!/usr/bin/env python

import os
import sys
import json
from collections import namedtuple
from tool import resolve_pointer, flatten
import sandboxjs

Args = namedtuple('Args', ['position', 'args'])
merge_args = lambda args: flatten([a.args for a in sorted(args, key=lambda x: x.position)])


def jseval(job, expression):
    if expression.startswith('{'):
        exp_tpl = '''{
        return function()%s();}
        '''
    else:
        exp_tpl = '''{
        return %s;}
        '''
    exp = exp_tpl % expression
    return sandboxjs.execjs(exp, "var $job = %s;" % json.dumps(job))


def resolve_transform(job, val):
    if not isinstance(val, dict) or val.get('@type') != 'Transform':
        return val
    lang = val.get('language')
    expr = val.get('value')
    if lang == 'javascript':
        return jseval(job, expr)
    elif lang == 'jsonpointer':
        return resolve_pointer(job, expr)
    else:
        raise Exception('Unknown language for Transform: %s' % lang)


def get_args(job, adapter, value=None, schema=None, key=None):
    position = adapter.get('position', 0)
    prefix = adapter.get('prefix')
    sep = adapter.get('separator', ' ')
    item_sep = adapter.get('itemSeparator')
    arg_val = adapter.get('argValue')
    pos = [position, key]

    if isinstance(arg_val, dict) and arg_val.get('@type') == 'Transform':
        value = resolve_transform(job, arg_val)
    elif isinstance(value, dict) and value.get('@type') == 'File':
        value = value.get('path')

    if value is None:
        return Args(pos, [])

    if isinstance(value, bool):
        return Args(pos, [prefix]) if value else Args(pos, [])

    if isinstance(value, dict):
        if not schema:
            return Args(pos, [])
        args = []
        for k, v in value.iteritems():
            item_schema = filter(lambda x: x['name'] == k, schema['fields'])[0]
            item_adapter = item_schema.get('adapter')
            if item_adapter is not None:
                args.append(get_args(job, item_adapter, v, item_schema, k))
        return Args(pos, merge_args(args))

    if isinstance(value, list):
        # TODO: complex item types
        items = map(lambda x: unicode(x) if not isinstance(x, dict) else x['path'], value)
        if item_sep:
            return Args(pos, get_args(job, adapter, item_sep.join(items)).args)
        if not prefix:
            return Args(pos, items)
        if sep == ' ':
            return Args(pos, flatten([prefix, item] for item in items))
        return Args(pos, [sep.join([prefix, item]) for item in items])

    value = unicode(value)
    if not prefix:
        return Args(pos, [value])
    if sep == ' ':
        return Args(pos, [prefix, value])
    return Args(pos, [sep.join([prefix, value])])


def get_proc_args_and_redirects(tool, job):
    adaptable_inputs = [i for i in tool.get('inputs', []) if 'adapter' in i.get('schema', {})]
    input_args = []
    for i in adaptable_inputs:
        inp_id = i['@id'][1:]
        inp_val = job['inputs'].get(inp_id)
        inp_adapter = i['schema']['adapter']
        input_args.append(get_args(job, inp_adapter, inp_val, i['schema'], inp_id))
    adapter_args = [get_args(job, a) for a in tool.get('adapters', [])]
    if isinstance(tool.get('baseCmd'), basestring):
        tool['baseCmd'] = [tool['baseCmd']]
    base_cmd = [resolve_transform(job, v) for v in tool['baseCmd']]
    argv = base_cmd + merge_args(input_args + adapter_args)
    stdin = resolve_transform(job, tool.get('stdin'))
    stdout = resolve_transform(job, tool.get('stdout'))
    return argv, stdin, stdout


def test(tool, job):
    ex = os.path.join(os.path.dirname(__file__), '../../examples/')
    with open(os.path.join(ex, tool)) as fp:
        tool = json.load(fp)
    with open(os.path.join(ex, job)) as fp:
        job = json.load(fp)
    argv, stdin, stdout = get_proc_args_and_redirects(tool, job)
    print ' '.join(argv), '<', stdin, '>', stdout


def conformance_test():
    tool, job = filter(lambda x: x[0] != '-', sys.argv[1:])
    assert os.path.isfile(tool)
    assert os.path.isfile(job)
    base_dir = filter(lambda x: x.startswith('--basedir='), sys.argv[1:])
    if base_dir:
        base_dir = base_dir[0][len('--basedir='):]

    with open(tool) as t, open(job) as j:
        tool = json.load(t)
        job = json.load(j)

    if base_dir:
        job['inputs'] = map_paths(job.get('inputs', {}), base_dir)

    argv, stdin, stdout = get_proc_args_and_redirects(tool, job)
    print json.dumps({
        'args': argv,
        'stdin': stdin,
        'stdout': stdout,
    })


def map_paths(obj, base_dir):
    if isinstance(obj, list):
        return [map_paths(i, base_dir) for i in obj]
    if not isinstance(obj, dict):
        return obj
    if obj.get('@type') == 'File':
        obj['path'] = os.path.join(base_dir, obj['path'])
        return obj
    return {k: map_paths(v, base_dir) for k, v in obj.iteritems()}


if __name__ == '__main__':
    if '--conformance-test' not in sys.argv:
        test('bwa-mem-tool.json', 'bwa-mem-job.json')
        test('cat1-tool.json', 'cat-n-job.json')
    else:
        conformance_test()
