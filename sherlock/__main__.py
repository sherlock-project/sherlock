#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""

if __name__ == "__main__":

    import controllers
    response = controllers.run()

    for key, value in response.items():
        print(f"Site: {key}, link: {value}")
