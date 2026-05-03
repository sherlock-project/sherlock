#!/usr/bin/env python3
# This module generates the listing of supported sites found in sites.mdx.
# It also organizes site keys in data.json using custom alphanumeric ordering.
import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_ENCODING = "utf-8"
SCHEMA_KEY = "$schema"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_DATA_PATH = REPO_ROOT / "sherlock_project" / "resources" / "data.json"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"


def site_sort_key(name: str) -> tuple[int, str]:
    """Sort names with digit-prefixed entries first, then alphabetically."""
    return (0 if name[:1].isdigit() else 1, name.casefold())


def build_sorted_data(data: dict[str, Any]) -> dict[str, Any]:
    """Return ordered data with schema first and sites custom-sorted."""
    schema_value = data.get(SCHEMA_KEY)
    site_items = [(k, v) for k, v in data.items() if k != SCHEMA_KEY]
    sorted_sites = sorted(site_items, key=lambda item: site_sort_key(item[0]))

    sorted_data: dict[str, Any] = {}
    if schema_value is not None:
        sorted_data[SCHEMA_KEY] = schema_value
    for key, value in sorted_sites:
        sorted_data[key] = value
    return sorted_data


def validate_sites(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Validate site entries and return them as sorted candidate tuples."""
    site_items: list[tuple[str, dict[str, Any]]] = []
    for site_name, site_info in data.items():
        if site_name == SCHEMA_KEY:
            continue
        if not isinstance(site_info, dict):
            raise ValueError(f"Site '{site_name}' has invalid metadata (expected object).")
        url_main = site_info.get("urlMain")
        if not isinstance(url_main, str) or not url_main.strip():
            raise ValueError(f"Site '{site_name}' is missing a valid 'urlMain' value.")
        site_items.append((site_name, site_info))
    return site_items


def render_sites_mdx(sites: list[tuple[str, dict[str, Any]]]) -> str:
    """Create the markdown list of supported sites."""
    lines = [
        "---",
        "title: 'List of supported sites'",
        "sidebarTitle: 'Supported sites'",
        "icon: 'globe'",
        f"description: 'Sherlock currently supports **{len(sites)}** sites'",
        "---",
        "",
    ]

    for social_network, info in sites:
        url_main = info["urlMain"]
        is_nsfw = " **(NSFW)**" if info.get("isNSFW") else ""
        lines.append(f"1. [{social_network}]({url_main}){is_nsfw}")

    lines.append("")
    return "\n".join(lines)


def atomic_write_text(path: Path, content: str) -> None:
    """Write content atomically to avoid partially-written files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding=DEFAULT_ENCODING,
            dir=path.parent,
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        os.replace(temp_file_path, path)
    finally:
        if temp_file_path is not None and temp_file_path.exists():
            temp_file_path.unlink()


def is_custom_sorted(data: dict[str, Any]) -> bool:
    """Return whether the incoming dict already follows expected order."""
    keys = list(data.keys())
    if not keys:
        return True
    if SCHEMA_KEY in data and keys[0] != SCHEMA_KEY:
        return False

    site_keys = [k for k in keys if k != SCHEMA_KEY]
    return site_keys == sorted(site_keys, key=site_sort_key)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate supported site listing and sort data.json keys."
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"Path to data.json (default: {DEFAULT_DATA_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory where sites.mdx will be written (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether data.json is custom-sorted without modifying files.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write sorted data.json and generated sites.mdx (default behavior).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check and args.write:
        raise SystemExit("Use either --check or --write, not both.")

    with args.data_file.open("r", encoding=DEFAULT_ENCODING) as data_file:
        data: dict[str, Any] = json.load(data_file)

    validate_sites(data)
    sorted_data = build_sorted_data(data)
    sorted_sites = [(k, v) for k, v in sorted_data.items() if k != SCHEMA_KEY]

    if args.check:
        if is_custom_sorted(data):
            print("OK: data.json is already sorted with digit-first ordering.")
            return 0
        print("FAIL: data.json is not sorted with digit-first ordering.")
        return 1

    output_file = args.output_dir / "sites.mdx"
    mdx_content = render_sites_mdx(sorted_sites)
    json_content = json.dumps(sorted_data, indent=2, ensure_ascii=False) + "\n"

    atomic_write_text(output_file, mdx_content)
    atomic_write_text(args.data_file, json_content)
    print(f"Finished updating supported site listing at {output_file}!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
