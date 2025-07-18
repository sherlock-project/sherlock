#!/usr/bin/env python3

"""
Sherlock Output Utilities

This module contains output-related utility functions for the Sherlock project.
"""

import os
import csv
import pandas as pd
from sherlock_project.result import QueryStatus


def get_output_file_path(username, args):
    """Determine the output file path based on arguments."""
    if args.output:
        return args.output
    elif args.folderoutput:
        os.makedirs(args.folderoutput, exist_ok=True)
        return os.path.join(args.folderoutput, f"{username}.txt")
    else:
        return f"{username}.txt"

def write_text_file(results, file_path):
    """Write results to a text file."""
    with open(file_path, "w", encoding="utf-8") as file:
        exists_counter = 0
        for website_name in results:
            dictionary = results[website_name]
            if dictionary.get("status").status == QueryStatus.CLAIMED:
                exists_counter += 1
                file.write(dictionary["url_user"] + "\n")
        file.write(f"Total Websites Username Detected On : {exists_counter}\n")

def write_csv_file(username, results, file_path, args):
    """Write results to a CSV file."""
    csv_path = file_path.replace('.txt', '.csv')
    if args.folderoutput:
        csv_path = os.path.join(args.folderoutput, f"{username}.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_report:
        writer = csv.writer(csv_report)
        writer.writerow(
            [
                "username",
                "name",
                "url_main",
                "url_user",
                "exists",
                "http_status",
                "response_time_s",
            ]
        )
        for site in results:
            if (
                args.print_found
                and not args.print_all
                and results[site]["status"].status != QueryStatus.CLAIMED
            ):
                continue

            response_time_s = results[site]["status"].query_time
            if response_time_s is None:
                response_time_s = ""
            writer.writerow(
                [
                    username,
                    site,
                    results[site]["url_main"],
                    results[site]["url_user"],
                    str(results[site]["status"].status),
                    results[site]["http_status"],
                    response_time_s,
                ]
            )

def write_xlsx_file(username, results, file_path, args):
    """Write results to an XLSX file."""
    xlsx_path = file_path.replace('.txt', '.xlsx')
    if args.folderoutput:
        xlsx_path = os.path.join(args.folderoutput, f"{username}.xlsx")

    usernames, names, url_main, url_user, exists, http_status, response_time_s = ([] for i in range(7))

    for site in results:
        if (
            args.print_found
            and not args.print_all
            and results[site]["status"].status != QueryStatus.CLAIMED
        ):
            continue

        time_val = results[site]["status"].query_time
        response_time_s.append(time_val if time_val is not None else "")
        usernames.append(username)
        names.append(site)
        url_main.append(results[site]["url_main"])
        url_user.append(results[site]["url_user"])
        exists.append(str(results[site]["status"].status))
        http_status.append(results[site]["http_status"])

    df = pd.DataFrame(
        {
            "username": usernames,
            "name": names,
            "url_main": url_main,
            "url_user": url_user,
            "exists": exists,
            "http_status": http_status,
            "response_time_s": response_time_s,
        }
    )
    df.to_excel(xlsx_path, sheet_name="sheet1", index=False)
