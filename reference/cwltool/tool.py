import os
import pprint
import json
import execjs
import pprint
import copy

from jsonschema.validators import Draft4Validator
from ref_resolver import from_url, resolve_pointer

module_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(module_dir, 'schemas/tool.json')) as f:
    tool_schema = json.load(f)
with open(os.path.join(module_dir, 'schemas/metaschema.json')) as f:
    metaschema = json.load(f)
tool_schema["properties"]["inputs"]["$ref"] = "file:%s/schemas/metaschema.json" % module_dir
tool_schema["properties"]["outputs"]["$ref"] = "file:%s/schemas/metaschema.json" % module_dir
tool_schema = Draft4Validator(tool_schema)

class Job(object):
    def run(self):
        pass

def each(l):
    if l is None:
        return []
    if isinstance(l, (list, tuple)):
        return l
    else:
        return [l]

# http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
def flatten(l, ltypes=(list, tuple)):
    if l is None:
        return []
    if not isinstance(l, ltypes):
        return [l]

    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def fix_file_type(t):
    if 'type' in t and t['type'] == "file":
        for a in metaschema["definitions"]["file"]:
            t[a] = metaschema["definitions"]["file"][a]
    for k in t:
        if isinstance(t[k], dict):
            fix_file_type(t[k])

def jseval(expression=None, job=None):
    if expression.startswith('{'):
        exp_tpl = '''function () {
        $job = %s;
        return function()%s();}()
        '''
    else:
        exp_tpl = '''function () {
        $job = %s;
        return %s;}()
        '''
    exp = exp_tpl % (json.dumps(job['job']), expression)
    return execjs.eval(exp)

def to_cli(value):
    if isinstance(value, dict) and 'path' in value:
        return value["path"]
    else:
        return str(value)

def adapt(adapter, job):
    if "value" in adapter:
        if "$expr" in adapter["value"]:
            value = jseval(adapter["value"]["$expr"]["value"], job)
        else:
            value = adapter["value"]
    elif "valueFrom" in adapter:
        value = resolve_pointer(job, adapter["valueFrom"])

    sep = adapter["separator"] if "separator" in adapter else ''

    value = [to_cli(v) for v in each(value)]

    if 'itemSeparator' in adapter:
        if adapter["prefix"]:
            l = [adapter["prefix"] + adapter['itemSeparator'].join(value)]
        else:
            l = [adapter['itemSeparator'].join(value)]
    elif 'prefix' in adapter:
        l = []
        for v in each(value):
            if sep == " ":
                l.append(adapter["prefix"])
                l.append(v)
            else:
                l.append(adapter["prefix"] + sep + v)
    else:
        l = [value]

    return l

class Tool(object):
    def __init__(self, toolpath_object):
        self.tool = toolpath_object["tool"]
        fix_file_type(self.tool)
        tool_schema.validate(self.tool)

    def job(self, joborder):
        inputs = joborder["job"]['inputs']
        Draft4Validator(self.tool['inputs']).validate(inputs)

        adapter = self.tool["adapter"]
        adapters = [{"order": -1000000, "value": adapter['baseCmd']}]

        for a in adapter["args"]:
            adapters.append(a)

        for k, v in self.tool['inputs']['properties'].items():
            if 'adapter' in v:
                a = copy.copy(v['adapter'])
            else:
                a = {}

            if not 'value' in a:
                a['valueFrom'] = "#/job/inputs/"+ k
            if not "order" in a:
                a["order"] = 1000000
            adapters.append(a)

        adapters.sort(key=lambda a: a["order"])
        pprint.pprint(adapters)

        j = Job()
        j.command_line = flatten(map(lambda adapter: adapt(adapter, joborder), adapters))

        if 'stdin' in adapter:
            j.stdin = flatten(adapt({"value": adapter['stdin']}, joborder))[0]
        else:
            j.stdin = None

        if 'stdout' in adapter:
            j.stdout = flatten(adapt({"value": adapter['stdout']}, joborder))[0]
        else:
            j.stdout = None

        return j
