import shlex
import subprocess
from kopf.testing import KopfRunner
import time
import unittest

class myTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_operator(self):

        with KopfRunner(['run', '-A', '--verbose', 'controller/handler.py']) as runner:
            # do something while the operator is running.

            subprocess.run("kubectl apply -f deploy/dev/obj.yaml", shell=True, check=True)
            time.sleep(1)  # give it some time to react and to sleep and to retry

            subprocess.run("kubectl delete -f deploy/dev/obj.yaml", shell=True, check=True)
            time.sleep(1)  # give it some time to react

        # print(runner.stdout)

        assert runner.exit_code == 0
        assert runner.exception is None
        assert "Handler 'create_or_resume' succeeded." in runner.stdout
        assert "Handler 'delete' succeeded." in runner.stdout

