import imp
import unittest
import sys
sys.path.append('../')
import sherlock as sh

checksymbols = []
checksymbols = ["_", "-", "."]

class TestMulripleUsernames(unittest.TestCase):
    def test_area(self):
        test_usernames = ["test{?}test" , "test{?feo" , "test"]
        for name in test_usernames:
            if(sh.CheckForParameter(name)):
                self.assertAlmostEqual(sh.MultipleUsernames(name), ["test_test" , "test-test" , "test.test"])
            else:
                self.assertAlmostEqual(name, name)