#!/usr/bin/env python

import os
import sys
import json
import logging
import tempfile
from collections import namedtuple
from tool import resolve_pointer, flatten
import sandboxjs
import avro.io
import avro.schema

Args = namedtuple('Args', ['position', 'args'])
merge_args = lambda args: flatten([a.args for a in sorted(args, key=lambda x: x.position)])


def jseval(job, expression, context=None):
    if expression.startswith('{'):
        exp_tpl = '''{
        return function()%s();}
        '''
    else:
        exp_tpl = '''{
        return %s;}
        '''
    exp = exp_tpl % expression
    return sandboxjs.execjs(exp, "var $job = %s, $self = %s;" % (json.dumps(job), json.dumps(context)))


def resolve_transform(job, val, context=None):
    if not isinstance(val, dict) or val.get('@type') != 'Transform':
        return val
    lang = val.get('language')
    expr = val.get('value')
    if lang == 'javascript':
        return jseval(job, expr, context)
    elif lang == 'jsonpointer':
        return resolve_pointer(job, expr)
    else:
        raise Exception('Unknown language for Transform: %s' % lang)


def get_args(job, adapter, value=None, schema=None, key=None, tool=None):
    if schema and 'adapter' in schema:
        adapter = schema['adapter']
    if adapter is None:
        return Args(None, [])

    position = adapter.get('position', 0)
    prefix = adapter.get('prefix')
    sep = adapter.get('separator', ' ')
    item_sep = adapter.get('itemSeparator')
    arg_val = adapter.get('argValue')
    pos = [position, key]

    if isinstance(arg_val, dict) and arg_val.get('@type') == 'Transform':
        value = resolve_transform(job, arg_val, value)
    elif isinstance(value, dict) and value.get('@type') == 'File':
        value = value.get('path')

    if value is None:
        return Args(pos, [])

    if isinstance(value, bool):
        if not prefix:
            raise Exception('Boolean value without prefix in adapter')
        return Args(pos, [prefix]) if value else Args(pos, [])

    if isinstance(value, dict):
        if not schema:
            return Args(pos, [])
        args = []
        for k, v in value.iteritems():
            field = filter(lambda x: x['name'] == k, schema['fields'])
            if not field:
                logging.error('Field not found in schema: "%s". Schema: %s', k, schema)
                continue
            field = field[0]
            field_adapter = field.get('adapter')
            field_schema = schema_by_name(field.get('type'), tool)
            args.append(get_args(job, field_adapter, v, field_schema, k, tool=tool))
        return Args(pos, merge_args(args))

    if isinstance(value, list):
        items = flatten([get_args(job, {}, i, schema_for_item(i, schema, tool), tool=tool).args for i in value])
        if item_sep:
            val = item_sep.join(items)
            if not prefix:
                return Args(pos, [val])
            return Args(pos, [prefix, val] if sep == ' ' else [sep.join([prefix, val])])
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


def schema_by_name(type_name, tool):
    if isinstance(type_name, dict):
        return type_name
    tds = filter(lambda x: x['name'] == type_name, tool.get('schemaDefs', []))
    return tds[0] if tds else None


def schema_for_item(value, array_schema, tool):
    if not array_schema:
        return None
    opts = array_schema.get('items', [])
    if not opts:
        return None
    if not isinstance(opts, list):
        opts = [opts]
    opts = [schema_by_name(opt, tool) for opt in opts]
    if len(opts) == 1:
        return opts[0]
    for opt in opts:
        sch = avro.schema.parse(json.dumps(opt))
        if avro.io.validate(sch, value):
            return opt
    return None


def get_proc_args_and_redirects(tool, job):
    adaptable_inputs = [i for i in tool.get('inputs', []) if 'adapter' in i.get('schema', {})]
    input_args = []
    for i in adaptable_inputs:
        inp_id = i['@id'][1:]
        inp_val = job['inputs'].get(inp_id)
        inp_adapter = i['schema']['adapter']
        input_args.append(get_args(job, inp_adapter, inp_val, i['schema'], inp_id, tool=tool))
    cli_adapter = tool['cliAdapter']
    adapter_args = [get_args(job, a, tool=tool) for a in cli_adapter.get('argAdapters', [])]
    if isinstance(cli_adapter.get('baseCmd'), basestring):
        cli_adapter['baseCmd'] = [cli_adapter['baseCmd']]
    base_cmd = [resolve_transform(job, v) for v in cli_adapter['baseCmd']]
    argv = base_cmd + merge_args(input_args + adapter_args)
    stdin = resolve_transform(job, cli_adapter.get('stdin'))
    stdout = resolve_transform(job, cli_adapter.get('stdout'))
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


def run(tool_path, job_path):
    with open(tool_path) as fpt, open(job_path) as fpj:
        tool = json.load(fpt)
        job = json.load(fpj)
    job = map_paths(job, os.path.join(os.path.dirname(__file__), '../../examples/'))
    argv, stdin, stdout = get_proc_args_and_redirects(tool, job)
    line = ' '.join(argv)
    if stdin:
        line += ' < ' + stdin
    if stdout:
        line += ' > ' + stdout
    print line
    job_dir = tempfile.mkdtemp()
    os.chdir(job_dir)
    if os.system(line):
        raise Exception('Process failed.')
    print os.listdir('.')


if __name__ == '__main__':
    if '--conformance-test' not in sys.argv:
        run(*sys.argv[1:])
        # test('bwa-mem-tool.json', 'bwa-mem-job.json')
        # test('cat1-tool.json', 'cat-n-job.json')
        # test('tmap-tool.json', 'tmap-job.json')
    else:
        conformance_test()
