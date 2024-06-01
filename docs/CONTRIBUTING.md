<p align=center>
  <br>
  <a href="https://sherlock-project.github.io/" target="_blank"><img src="https://user-images.githubusercontent.com/27065646/53551960-ae4dff80-3b3a-11e9-9075-cef786c69364.png"/></a>
  <br>
</p>

<p align="center">
  <a href="https://github.com/sherlock-project/sherlock">Home</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/sherlock-project/sherlock#installation">Installation</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/sherlock-project/sherlock#usage">Usage</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/sherlock-project/sherlock/docs/INSTALL.md#docker">Docker</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <strong><a href="https://github.com/sherlock-project/sherlock/docs/CONTRIBUTING.md">Contributing</a></strong>
</p>

# How to contribute to Sherlock

We would love to have you help us with the development of Sherlock. Each and every contribution is greatly valued!

Here are some things we would appreciate your help on:
1. [Adding targets](#adding-targets)
1. [Cleaning up existing targets](#removing-targets)
1. [Restoring previously removed targets](#restoring-targets)

## Adding targets

Please look at the Wiki entry on [adding new sites][wiki_new_sites] to understand the issues.

All new sites that are added to Sherlock need to have an existing (already claimed) username included in their definition. The linked Wiki page describes this in more detail. This inclusion allows us to run unit tests and prevent regression.

Contributors are *required* to test any new sites for both false positives and false negatives. Contributors are *encouraged* to run unit tests as well.

Contributors do not have to run the [site_list.py](/site_list.py) script, as it's ran automagically on master after each manifest change.

## Removing targets

If there are performance problems with a site (e.g. slow to respond, unreliable uptime, ...), then
the site may be removed from the list. The [removed_sites.md][file_removed_md] file contains sites that were included at one time in Sherlock, but had to be removed for one reason or another.

If a site has *occasional* performance problems, but is otherwise accurate, it may be preferable to add a test to weed out false positives rather than removing it.

## Restoring targets

Likely our biggest backlog. If you can propose a functional query that complies with [#Adding targets](#adding-targets) that would shrink our [removed sites list][file_removed_md], that would be greatly appreciated.

## Adding New Functionality

Contributors that would like to add a feature to Sherlock should open an new [issue][issues_new], proposing their idea. Indicate that you would like to make a Pull Request for said feature.

Creating an Issue prior to opening a PR helps with tracking, discussions, and avoids hurt feelings if for whatever reason we don't feel that a feature is compatible with the project.

Please ensure that the content on your branch passes all tests before submitting a pull request.

# Coverage and Unit Tests

Thank you for contributing to Sherlock!

Before creating a pull request with new development, please run the tests
to ensure that everything is working great.  It would also be a good idea to run the tests
before starting development to distinguish problems between your
environment and the Sherlock software.

The following is an example of the command line to run all the tests for
Sherlock.  This invocation hides the progress text that Sherlock normally
outputs, and instead shows the verbose output of the tests.

```console
# Assumes current working directory is respository root
$ python3 -m unittest tests.all --verbose
```

Unfortunately, some of the sites that Sherlock checks are not always reliable, so it is common
to get response problems.  Any problems in connection will show up as warnings in the tests instead of true errors.

If some sites are failing due to connection problems (site is down, in maintenance, etc) you can exclude them from tests by creating a `tests/.excluded_sites` file with a list of sites to ignore (one site name per line).

## Coverage for new features

Contributors that add new features are *encouraged* make an attempt at creating unit tests for them, as well. Not all contributions are suitable for unit tests, but when it's doable, it helps prevent regression.

<!-- Reference Links -->

[wiki_new_sites]: https://github.com/sherlock-project/sherlock/wiki/Adding-Sites-To-Sherlock
[file_removed_md]: /removed_sites.md
[issues_new]: https://github.com/sherlock-project/sherlock/issues/new/choose