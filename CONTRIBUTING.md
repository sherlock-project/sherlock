# How To Contribute To Sherlock
First off, thank you for the help!

There are many ways to contribute.  Here is some high level grouping.

## Adding New Sites

Please look at the Wiki entry on
[adding new sites](https://github.com/TheYahya/sherlock/wiki/Adding-Sites-To-Sherlock)
to understand the issues.

Any new sites that are added need to have a username that has been claimed, and one
that is unclaimed documented in the site data.  This allows the regression tests
to ensure that everything is working.

In regards to adult sites (e.g. PornHub), we have agreed to not include them in Sherlock.  
However, we do understand that some users desires this support.  The data.json file is easy to add to, 
so users will be able to maintain their own forks to have this support. This is not ideal.  
Maybe there could be another repo with an adult data.json? That would avoid forks getting out of date.

## Adding New Functionality

Please ensure that the content on your branch passes all tests before submitting a pull request.
