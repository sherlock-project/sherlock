## Fixes #2992

**Problem:** Passing `--output results.txt` without `--txt` creates no output file and shows no error.

**Root cause:** The write block is guarded exclusively by `args.output_txt`, but `result_file` is already correctly set by `args.output`.

**Fix:** Change condition from `if args.output_txt:` to `if args.output_txt or args.output:`
