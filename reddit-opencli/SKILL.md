---
name: reddit-opencli
description: Use this skill for Reddit workflows through opencli-rs, including subreddit and keyword research, frontpage/popular scans, reading posts and comments, monitoring new Reddit posts, and account write actions such as commenting, upvoting, downvoting, saving, subscribing, and unsubscribing. Trigger when the user asks Codex to browse, research, summarize, monitor, or interact with Reddit, especially when Chrome login state or opencli-rs should be reused.
---

# Reddit OpenCLI

Use `opencli-rs` as the Reddit backend. Prefer the bundled wrapper scripts for
repeatable workflows and safer writes.

## First checks

Run the verifier before any serious work:

```bash
bash reddit-opencli/scripts/ensure_opencli.sh
opencli-rs doctor
```

If `opencli-rs doctor` reports that the Chrome extension is not connected, stop
and tell the user to enable the OpenCLI Chrome extension. Reddit browser-mode
commands will not work reliably without that bridge.

For detailed setup and troubleshooting, read
`references/reddit-opencli-reference.md`.

## Research workflow

Use `redditctl.py research` for multi-source collection, de-duplication, and
Markdown/JSON output:

```bash
python3 reddit-opencli/scripts/redditctl.py research \
  --subreddit LocalLLaMA \
  --subreddit selfhosted \
  --query "agentic coding" \
  --limit 25 \
  --format md
```

Use JSON when another script or analysis step will consume the result:

```bash
python3 reddit-opencli/scripts/redditctl.py research --subreddit rust --limit 20 --format json
```

## Thread workflow

Use `redditctl.py thread` to read a post and comments:

```bash
python3 reddit-opencli/scripts/redditctl.py thread "<reddit-url-or-post-id>" \
  --limit 30 \
  --depth 2 \
  --sort best \
  --format md
```

Summarize findings with direct Reddit links and separate post facts from
inference.

## Watch workflow

Use `redditctl.py watch` when the user wants updates since the last run:

```bash
python3 reddit-opencli/scripts/redditctl.py watch \
  --subreddit openai \
  --query "agents" \
  --limit 25 \
  --format md
```

The watch command stores a local state file under
`${XDG_STATE_HOME:-~/.local/state}/kk-reddit/watch/`.

## Write actions

Supported first-class actions:

- `comment`
- `upvote`
- `downvote`
- `unvote`
- `save`
- `unsave`
- `subscribe`
- `unsubscribe`

Never execute a write action without showing the user:

- the exact target post/subreddit
- the comment text when applicable
- the exact `opencli-rs` command that will run
- the account/platform risk that Reddit automation can trigger

First generate a preview without `--yes`:

```bash
python3 reddit-opencli/scripts/redditctl.py act comment "<post-url-or-id>" --text "Draft comment"
```

After the user explicitly confirms the exact action, run the same command with
`--yes`:

```bash
python3 reddit-opencli/scripts/redditctl.py act comment "<post-url-or-id>" --text "Draft comment" --yes
```

## Fallback rule

If a Reddit command fails because the Chrome extension is missing or the user is
not logged in, do not silently switch to unrelated web scraping. Report the
blocked state and ask the user to connect Chrome/OpenCLI or log in to Reddit.

