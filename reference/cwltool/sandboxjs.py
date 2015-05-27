import subprocess
import json
import threading

class JavascriptException(Exception):
    pass

def execjs(js, jslib):
    nodejs = subprocess.Popen(["nodejs"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    fn = "\"use strict\";%s\n(function()%s)()" % (jslib, js if isinstance(js, basestring) and len(js) > 1 and js[0] == '{' else ("{return (%s);}" % js))
    script = "console.log(JSON.stringify(require(\"vm\").runInNewContext(%s, {})))" % json.dumps(fn)

    #print script

    def term():
        try:
            nodejs.terminate()
        except OSError:
            pass

    # Time out after 5 seconds
    tm = threading.Timer(5, term)
    tm.start()

    stdoutdata, stderrdata = nodejs.communicate(script)
    tm.cancel()

    if stderrdata.strip() or nodejs.returncode != 0:
        raise JavascriptException(script + "\n" + stderrdata)
    else:
        return json.loads(stdoutdata)
