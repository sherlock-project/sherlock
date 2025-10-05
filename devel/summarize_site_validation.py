#!/usr/bin/env python
# This module summarizes the results of site validation tests queued by
# workflow validate_modified_targets for presentation in Issue comments.

from defusedxml import ElementTree as ET
import sys
from pathlib import Path

def summarize_junit_xml(xml_path: Path) -> str:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    suite = root.find('testsuite')

    pass_message: str = ":heavy_check_mark: &nbsp; Pass"
    fail_message: str = ":x: &nbsp; Fail"

    if suite is None:
        raise ValueError("Invalid JUnit XML: No testsuite found")

    summary_lines: list[str] = []
    summary_lines.append("#### Automatic validation of changes\n")
    summary_lines.append("| Target | F+ Check | F- Check |")
    summary_lines.append("|---|---|---|")

    failures = int(suite.get('failures', 0))
    errors_detected: bool = False

    results: dict[str, dict[str, str]] = {}

    for testcase in suite.findall('testcase'):
        test_name = testcase.get('name').split('[')[0]
        site_name = testcase.get('name').split('[')[1].rstrip(']')
        failure = testcase.find('failure')
        error = testcase.find('error')

        if site_name not in results:
            results[site_name] = {}

        if test_name == "test_false_neg":
            results[site_name]['F- Check'] = pass_message if failure is None and error is None else fail_message
        elif test_name == "test_false_pos":
            results[site_name]['F+ Check'] = pass_message if failure is None and error is None else fail_message

        if error is not None:
            errors_detected = True

    for result in results:
        summary_lines.append(f"| {result} | {results[result].get('F+ Check', 'Error!')} | {results[result].get('F- Check', 'Error!')} |")

    if failures > 0:
        summary_lines.append("\n___\n" +
            "\nFailures were detected on at least one updated target. Commits containing accuracy failures" +
            " will often not be merged (unless a rationale is provided, such as false negatives due to regional differences).")

    if errors_detected:
        summary_lines.append("\n___\n" +
            "\n**Errors were detected during validation. Please review the workflow logs.**")

    return "\n".join(summary_lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: summarize_site_validation.py <junit-xml-file>")
        sys.exit(1)

    xml_path: Path = Path(sys.argv[1])
    if not xml_path.is_file():
        print(f"Error: File '{xml_path}' does not exist.")
        sys.exit(1)

    summary: str = summarize_junit_xml(xml_path)
    print(summary)
