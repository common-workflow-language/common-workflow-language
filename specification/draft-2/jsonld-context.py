#!/usr/bin/env python

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
cwl_avsc = os.path.join(module_dir, '../../schemas/draft-2/cwl-avro.yml')

context = {
    "cwl": "http://github.com/common-workflow-language#",
    "avro": "http://github.com/common-workflow-language#avro/",
    "wfdesc": "http://purl.org/wf4ever/wfdesc#",
    "dct": "http://purl.org/dc/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
}

def pred(datatype, field, name):
    v = None
    if field and "jsonldPredicate" in field:
        v = field["jsonldPredicate"]
    elif field and "jsonldPrefix" in field:
        v = "%s:%s" % (field["jsonldPrefix"], name)
    elif "jsonldPrefix" in datatype:
        v = "%s:%s" % (datatype["jsonldPrefix"], name)
    else:
        v = "cwl:%s" % (name)
    if v:
        if name in context:
            if context[name] != v:
                raise Exception("Predicate collision on %s, %s != %s" % (name, context[name], v))
        else:
            context[name] = v

with open(cwl_avsc) as f:
    j = yaml.load(f)
    for t in j:
        if t["type"] == "record":
            if t["name"] in context:
                raise Exception("Collision on %s" % t["name"])

            if "jsonldPrefix" in t:
                context[t["name"]] = "%s:%s" % (t["jsonldPrefix"], t["name"])
            else:
                context[t["name"]] = "cwl:%s" % (t["name"])

            for i in t["fields"]:
                pred(t, i, i["name"])
        elif t["type"] == "enum":
            for i in t["symbols"]:
                pred(t, None, i)

print json.dumps(context, indent=4, sort_keys=True)
