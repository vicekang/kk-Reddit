# Reddit OpenCLI Reference

Load this reference when the user needs detailed Reddit command syntax,
installation troubleshooting, or write-action handling.

## Backend

Use only:

```bash
opencli reddit ...
```

Do not prefer browser automation over OpenCLI for Reddit unless the OpenCLI path
is blocked and the user approves a fallback.

## Useful Direct Commands

```bash
opencli reddit hot --subreddit rust --limit 20 -f json
opencli reddit frontpage --limit 20 -f json
opencli reddit popular --limit 20 -f json
opencli reddit home --limit 20 -f json
opencli reddit search "local llm" --limit 20 --sort relevance --time month -f json
opencli reddit subreddit LocalLLaMA --sort top --time week --limit 20 -f json
opencli reddit read "https://www.reddit.com/r/rust/comments/..." --limit 25 --depth 2 --sort best -f json
opencli reddit saved --limit 20 -f json
opencli reddit subscribed --limit 20 -f json
opencli reddit upvoted --limit 20 -f json
opencli reddit whoami -f json
opencli reddit user "spez" -f json
opencli reddit user-posts "spez" --limit 20 -f json
opencli reddit user-comments "spez" --limit 20 -f json
```

## Write Command Mapping

OpenCLI write commands use a post id/fullname for post actions. The wrapper
accepts a full Reddit URL and extracts the post id when possible.

```bash
opencli reddit comment <post-id> "comment text" -f json
opencli reddit upvote <post-id> --direction up -f json
opencli reddit upvote <post-id> --direction down -f json
opencli reddit upvote <post-id> --direction none -f json
opencli reddit save <post-id> -f json
opencli reddit save <post-id> --undo true -f json
opencli reddit subscribe <subreddit> -f json
opencli reddit subscribe <subreddit> --undo true -f json
```

The skill must show a preview and wait for explicit confirmation before adding
`--yes` to the wrapper command.

## Chrome Extension

Reddit commands run through browser mode. If `opencli doctor` reports an
extension problem, Reddit commands may fail.

Install/update OpenCLI:

```bash
npm install -g @jackwener/opencli
```

Check for extension assets:

```bash
find ~/.opencli/extensions -maxdepth 1 -type d -name 'opencli-extension-v*' -print
```

Chrome extension installation cannot be fully automated from a shell script
without weakening Chrome's extension safety model.

## Output Handling

Use `-f json` for all data collection. The wrapper normalizes common fields:

- `id`
- `fullname`
- `title`
- `author`
- `subreddit`
- `url`
- `permalink`
- `score`
- `comments`
- `created`
- `source`

If the backend returns a different shape, preserve the raw row in the JSON
payload and summarize cautiously.

## Failure Handling

- If the Chrome extension is disconnected or unstable, report that exact blocker.
- If Reddit login is missing, ask the user to log in to Reddit in Chrome.
- If a write action fails, do not retry repeatedly; report command, target, and
  stderr/stdout.
- If a read command returns empty data, verify subreddit/query spelling and run
  a smaller smoke test.

