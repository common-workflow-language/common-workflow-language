import yaml
import sys

def scan(base, doc):
    r = []
    if isinstance(doc, dict):
        if "$import" in doc:
            p = os.path.join(base, doc["$import"])
            with open(sys.argv[1]) as f:
                r.append({
                    "class": "File",
                    "path": p,
                    "secondaryFiles": scan(p, yaml.load(f))
                })
    if isinstance(doc, list):
        for d in doc:
            r.extend(base, d)
    return r

with open(sys.argv[1]) as f:
    print {
        "class": "File",
        "path": sys.argv[1],
        "secondaryFiles": scan(sys.argv[1], yaml.load(f))
    }
