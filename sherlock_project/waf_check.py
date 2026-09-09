import requests
import yaml


NUCLEI_FINGERPRINT_URL: str = "https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/refs/heads/main/http/global-matchers/global-waf-detect.yaml"

def _check_nuclei_regex(matcher: dict[str,str|list[str]], response: requests.Response) -> bool:
    import re

    and_cond: bool = matcher.get('condition', '') == 'and'

    target_text: str
    if matcher['part'] == 'body':
        target_text = response.text
    elif matcher['part'] == 'header':
        target_text = str(response.headers)
    else:
        target_text = response.text + str(response.headers)

    for regex in matcher['regex']:
        if re.search(regex, target_text):
            if not and_cond:
                return True
        else:
            break
    else:
        # `and` conditions will cycle, resulting in this default return True
        # unless an early failed detection breaks the loop (resulting in False)
        return True
    return False

def _check_nuclei_words(matcher: dict[str,str|list[str]], response: requests.Response) -> bool:
    and_cond: bool = matcher.get('condition', '') == 'and'

    target_text: str
    if matcher['part'] == 'body':
        target_text = response.text
    elif matcher['part'] == 'header':
        target_text = str(response.headers)
    else:
        target_text = response.text + str(response.headers)

    for word in matcher['words']:
        if word in target_text:
            if not and_cond:
                return True
        else:
            break
    else:
        # `and` conditions will cycle, resulting in this default return True
        # unless an early failed detection breaks the loop (resulting in False)
        return True
    return False

def fetch_nuclei_fingerprints() -> list[dict[str,str|list[str]]] | None:
    """Fetch the latest Nuclei WAF fingerprints from the official repository."""
    try:
        response = requests.get(NUCLEI_FINGERPRINT_URL, timeout=10)
        response.raise_for_status()
        raw = yaml.safe_load(response.text)
        fingerprints: list[dict[str,str|list[str]]] = raw['http'][0]['matchers']
        return fingerprints
    except requests.RequestException as e:
        print(f"Error fetching Nuclei fingerprints: {e}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML data: {e}")
        return None

def nuclei_check(response: requests.Response, fingerprints: list[dict[str,str|list[str]]]) -> bool:
    """Check if the response matches any of the WAF fingerprints.

    Keyword arguments:
    response -- The HTTP response to check.
    fingerprints -- The list of Nuclei WAF fingerprints to check against.

    Returns True if a WAF is detected, False otherwise.
    """
    for matcher in fingerprints:
        if matcher['type'] == 'word':
            return _check_nuclei_words(matcher, response)
        elif matcher['type'] == 'regex':
            return _check_nuclei_regex(matcher, response)
    return False
