import os
import unittest
from unittest.mock import patch, Mock
import requests
from requests.structures import CaseInsensitiveDict
import yaml

from sherlock_project import waf_check


TEMPLATE_BODY_PATH: str = os.path.join(os.path.dirname(__file__), 'mocks', 'global_waf_detect.yaml')

def side_effect(url, **kwargs) -> Mock:
    if url == waf_check.NUCLEI_FINGERPRINT_URL:
        with open(TEMPLATE_BODY_PATH, 'r', encoding='utf-8') as file:
            template_body: str = file.read()
        mock_response: Mock = Mock()
        mock_response.status_code = 200
        mock_response.text = template_body
        return mock_response
    raise RuntimeError("Unexpected URL")

class TestWafCheck(unittest.TestCase):

    @patch('sherlock_project.waf_check.requests.get')
    def test_fetch_nuclei_fingerprints(self, mock_requests_get): # type: ignore
        mock_requests_get.side_effect = side_effect

        result = waf_check.fetch_nuclei_fingerprints()

        with open(TEMPLATE_BODY_PATH, 'r', encoding='utf-8') as file:
            template_body: str = file.read()

        expected: list[dict[str, str | list[str]]] = yaml.safe_load(template_body)['http'][0]['matchers']
        self.assertEqual(result, expected)

    def test_nuclei_regex_check(self):
        mock_res: requests.Response = requests.Response()
        mock_res.status_code = 200
        mock_res._content = b"This is a test response with Test-Regex in the body."
        mock_res.headers = CaseInsensitiveDict({
            'Content-Type': 'text/html',
            'Server': 'TestServer'
        })
        matcher: dict[str, str | list[str]] = {
            'type': 'regex',
            'name': 'test-regex',
            'part': 'body',
            'regex': [r'(?i)not-present'],
            'condition': 'or'
        }
        self.assertFalse(waf_check._check_nuclei_regex(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['regex'] = [r'(?i)TeSt-REgEx']
        self.assertTrue(waf_check._check_nuclei_regex(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['regex'] = [r'(?i)TeSt-REgEx', r'(?i)Not-Present']
        self.assertTrue(waf_check._check_nuclei_regex(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['condition'] = 'and'
        self.assertFalse(waf_check._check_nuclei_regex(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['part'] = 'header'
        matcher['regex'] = [r'(?i)testserver']
        self.assertTrue(waf_check._check_nuclei_regex(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['part'] = 'response'
        self.assertTrue(waf_check._check_nuclei_regex(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['regex'] = [r'(?i)not-present']
        self.assertFalse(waf_check._check_nuclei_regex(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

    def test_nuclei_words_check(self):
        mock_res: requests.Response = requests.Response()
        mock_res.status_code = 200
        mock_res._content = b"This is a test response with test-words in the body."
        mock_res.headers = CaseInsensitiveDict({
            'Content-Type': 'text/html',
            'Server': 'TestServer'
        })
        matcher: dict[str, str | list[str]] = {
            'type': 'word',
            'name': 'test-word',
            'part': 'body',
            'words': ['not-present'],
            'condition': 'or'
        }
        self.assertFalse(waf_check._check_nuclei_words(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['words'] = ['test-word']
        self.assertTrue(waf_check._check_nuclei_words(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['words'] = ['test-word', 'Not-Present']
        self.assertTrue(waf_check._check_nuclei_words(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['condition'] = 'and'
        self.assertFalse(waf_check._check_nuclei_words(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['part'] = 'header'
        matcher['words'] = ['testserver']
        self.assertFalse(waf_check._check_nuclei_words(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['words'] = ['TestServer']
        self.assertTrue(waf_check._check_nuclei_words(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]

        matcher['part'] = 'response'
        self.assertTrue(waf_check._check_nuclei_words(matcher, mock_res)) # pyright: ignore[reportPrivateUsage]
