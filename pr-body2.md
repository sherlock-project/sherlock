Fixes #2990

Problem: When scanning multiple usernames, the result counter accumulates across all usernames because it uses a module-level globvar that is never reset between scans.

Root cause: notify.py defines globvar = 0 at module level. countResults() increments it, but it persists across all username scans for the process lifetime.

Fix:
- Removed module-level globvar
- Added self._result_count = 0 initialized in QueryNotifyPrint.__init__
- Updated countResults() to use self._result_count
- Updated finish() to read self._result_count directly instead of countResults() - 1
