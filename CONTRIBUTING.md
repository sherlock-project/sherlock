# How To Contribute To Sherlock
First off, thank you for the help!

There are many ways to contribute.  Here is some high level grouping.

## Adding New Sites

Please look at the Wiki entry on
[adding new sites](https://github.com/sherlock-project/sherlock/wiki/Adding-Sites-To-Sherlock)
to understand the issues.

Any new sites that are added need to have a username that has been claimed, and one
that is unclaimed documented in the site data.  This allows the regression tests
to ensure that everything is working.

It is required that a contributor test any new sites by either running the full tests, or running
a site-specific query against the claimed and unclaimed usernames.

It is not required that a contributor run the 
[site_list.py](https://github.com/sherlock-project/sherlock/blob/master/site_list.py)
script.

If there are performance problems with a site (e.g. slow to respond, unreliable uptime, ...), then
the site may be removed from the list.  The 
[removed_sites.md](https://github.com/sherlock-project/sherlock/blob/master/removed_sites.md)
file contains sites that were included at one time in Sherlock, but had to be removed for
one reason or another.

## Adding New Functionality

Please ensure that the content on your branch passes all tests before submitting a pull request.
