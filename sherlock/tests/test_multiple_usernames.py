import importlib
import unittest
import sys
sys.path.append('../')
import sherlock as sh

checksymbols = []
checksymbols = ["_", "-", "."]

"""Test for multiple usernames.

        This test ensures that the function multiple_usernames works properly. More specific,
        different scenarios are tested and only usernames that contain this specific sequence: {?} 
        should return positive.
      
        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        """
class TestMultipleUsernames(unittest.TestCase):
    def test_area(self):
        test_usernames = ["test{?}test" , "test{?feo" , "test"]
        for name in test_usernames:
            if(sh.check_for_parameter(name)):
                self.assertAlmostEqual(sh.multiple_usernames(name), ["test_test" , "test-test" , "test.test"])
            else:
                self.assertAlmostEqual(name, name)