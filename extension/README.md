# Reddit Extension Design Notes

This repository does not ship a replacement Chrome extension in v1.

Reddit browser-mode commands depend on the OpenCLI browser bridge. A separate
Reddit content-script extension would not automatically be used by `opencli`
unless it implements the same bridge protocol or OpenCLI adds support for it.

## Possible v2 Scope

A Reddit-optimized extension could add:

- Stable post and comment extraction helpers for Reddit's changing DOM.
- Better logged-in account status detection.
- Safer write previews inside the page before comment/upvote/subscribe actions.
- Structured thread export with comment tree metadata.
- Rate-limit and automation-risk warnings.

## Integration Options

1. Upstream bridge-compatible extension
   - Best fit if the goal is to keep using `opencli reddit ...`.
   - Requires matching the OpenCLI daemon protocol.

2. Companion extension plus OpenCLI adapter changes
   - Good fit if upstream accepts a Reddit-specific helper path.
   - Requires adapter changes in OpenCLI.

3. Independent extension backend
   - Useful for browser-only workflows.
   - A different backend from this skill's `opencli` path.

For now, use the OpenCLI extension documented in `docs/CHROME_EXTENSION.md`.

