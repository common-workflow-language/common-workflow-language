import unittest
import cwltool.draft2tool as tool
from cwltool.ref_resolver import from_url

class TestExamples(unittest.TestCase):
    def test_cat1(self):
        pass
        #t = tool.Tool(from_url("../examples/draft-2/cat4-tool.json"))
        #job = t.job(from_url("../examples/draft-2/cat-job.json"), basedir="../examples/draft-2")
        #result = job.run()
        #print result


if __name__ == '__main__':
    unittest.main()
