import unittest
from cwltool import tool
from cwltool.ref_resolver import from_url, resolve_pointer

class TestExamples(unittest.TestCase):
    def test_job_order(self):
        t = tool.Tool(from_url("../examples/bwa-mem-tool.json"))
        job = t.job(from_url("../examples/bwa-mem-job.json"))
        self.assertEqual(job.command_line, ['bwa',
                                            'mem',
                                            '-t4',
                                            '-m',
                                            '3',
                                            '-I1,2,3,4',
                                            './rabix/tests/test-files/chr20.fa',
                                            './rabix/tests/test-files/example_human_Illumina.pe_1.fastq',
                                            './rabix/tests/test-files/example_human_Illumina.pe_2.fastq'])


if __name__ == '__main__':
    unittest.main()
