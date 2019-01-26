import json
import yaml

from sherlock_test import framework
from unittest import TestCase
from sherlock.core import Data

def setup_module():
    framework.clean()
    _fromFile_json = framework.create("test_fromFile.json")
    _fromFile_yaml = framework.create("test_fromFile.yaml")

    fromFileDict = {
        "Instagram": {
            "url": "https://www.instagram.com/{}",
            "urlMain": "https://www.instagram.com/",
            "errorType": "message",
            "errorMsg": "The link you followed may be broken"
        },
        "Twitter": {
            "url": "https://www.twitter.com/{}",
            "urlMain": "https://www.twitter.com/",
            "errorType": "message",
            "errorMsg": "page doesn’t exist"
        },
        "Facebook": {
            "url": "https://www.facebook.com/{}",
            "urlMain": "https://www.facebook.com/",
            "errorType": "status_code",
            "regexCheck": "^[a-zA-Z0-9]{4,49}(?<!.com|.org|.net)$"
        }
    }

    with open(_fromFile_json, "w") as f:
        f.write(json.dumps(fromFileDict))

    with open(_fromFile_yaml, "w") as f:
        f.write(yaml.dumps(fromFileDict))


def teardown_module():
    framework.clean()

class TestData(TestCase):



    def test_fromFile(self):
        # TODO Write test code

        Data.fromFile("")


        self.fail()

    def test_keys(self):
        # TODO Write test code
        self.fail()

    def test_byindex(self):
        # TODO Write test code
        self.fail()