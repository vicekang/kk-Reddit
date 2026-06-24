# Reddit Extension Design Notes

This repository does not ship a replacement Chrome extension in v1.

Reason: the `opencli-rs reddit ...` commands depend on the OpenCLI browser
bridge. A separate Reddit content-script extension would not automatically be
used by `opencli-rs` unless it implements the same daemon protocol or `opencli-rs`
adds support for it.

## Possible v2 scope

A Reddit-optimized extension could add:

- Stable post and comment extraction helpers for Reddit's changing DOM.
- Better logged-in account status detection.
- Safer write previews inside the page before comment/upvote/subscribe actions.
- Structured thread export with comment tree metadata.
- Rate-limit and automation-risk warnings.

## Integration options

1. Upstream bridge-compatible extension
   - Best fit if the goal is to keep using `opencli-rs reddit ...`.
   - Requires matching the OpenCLI daemon protocol.

2. Companion extension plus opencli-rs adapter changes
   - Good fit if upstream accepts a Reddit-specific helper path.
   - Requires adapter changes in `opencli-rs`.

3. Independent extension backend
   - Useful for browser-only workflows.
   - Not a direct replacement for this skill's `opencli-rs` backend.

For now, use the OpenCLI extension documented in `docs/CHROME_EXTENSION.md`.

