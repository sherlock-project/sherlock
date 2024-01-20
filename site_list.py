#!/usr/bin/env python
import json
import os

def load_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading data: {e}")
        return None

def write_markdown_file(social_networks, file_path):
    lines = [
        f"1. ![](https://www.google.com/s2/favicons?domain={info['urlMain']}) [{network}]({info['urlMain']}) {'**(NSFW)**' if info.get('isNSFW') else ''}\n"
        for network, info in social_networks
    ]
    with open(file_path, "w") as file:
        file.write(f"## List Of Supported Sites ({len(social_networks)} Sites In Total!)\n")
        file.writelines(lines)

def save_sorted_data(data, file_path):
    with open(file_path, "w") as file:
        sorted_data = json.dumps(data, indent=2, sort_keys=True)
        file.write(sorted_data)
        file.write("\n")

def main():
    data_file_path = "sherlock/resources/data.json"
    md_file_path = "sites.md"

    data = load_data(data_file_path)
    if data is None:
        return

    sorted_social_networks = sorted(data.items())
    write_markdown_file(sorted_social_networks, md_file_path)
    save_sorted_data(data, data_file_path)

    print("Finished updating supported site listing!")

if __name__ == "__main__":
    main()
