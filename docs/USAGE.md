# Usage Guide

This guide shows how to use the `reddit-opencli` skill and its wrapper script.

All examples assume the skill is installed at:

```text
${CODEX_HOME:-$HOME/.codex}/skills/reddit-opencli
```

From a cloned repository, replace that path with `./reddit-opencli`.

## Verify the environment

```bash
bash reddit-opencli/scripts/ensure_opencli.sh
python3 reddit-opencli/scripts/redditctl.py check
```

Force the OpenCLI backend:

```bash
KK_REDDIT_BACKEND=opencli python3 reddit-opencli/scripts/redditctl.py check
```

Optional smoke test:

```bash
python3 reddit-opencli/scripts/redditctl.py check --smoke-subreddit rust --limit 3
```

If the smoke test fails with "Chrome extension not connected", follow
[Chrome extension setup](CHROME_EXTENSION.md).

## Research subreddits

Collect hot, new, rising, and top posts from one subreddit:

```bash
python3 reddit-opencli/scripts/redditctl.py research \
  --subreddit LocalLLaMA \
  --limit 25 \
  --format md
```

Compare multiple subreddits:

```bash
python3 reddit-opencli/scripts/redditctl.py research \
  --subreddit LocalLLaMA \
  --subreddit selfhosted \
  --subreddit openai \
  --sorts hot,top,rising \
  --time week \
  --limit 20 \
  --format md
```

Write JSON to a file:

```bash
python3 reddit-opencli/scripts/redditctl.py research \
  --subreddit rust \
  --limit 30 \
  --format json \
  --output outputs/rust-reddit.json
```

## Search Reddit

Search all Reddit:

```bash
python3 reddit-opencli/scripts/redditctl.py research \
  --query "agentic coding" \
  --search-sort relevance \
  --time month \
  --limit 20 \
  --format md
```

Search inside a subreddit:

```bash
python3 reddit-opencli/scripts/redditctl.py research \
  --query "cursor" \
  --search-subreddit LocalLLaMA \
  --search-sort comments \
  --time year \
  --limit 20 \
  --format md
```

Include frontpage and popular:

```bash
python3 reddit-opencli/scripts/redditctl.py research \
  --include-frontpage \
  --include-popular \
  --limit 20 \
  --format md
```

## Read a thread

```bash
python3 reddit-opencli/scripts/redditctl.py thread \
  "https://www.reddit.com/r/rust/comments/..." \
  --limit 30 \
  --depth 2 \
  --replies 5 \
  --sort best \
  --format md
```

Use `--format json` when Codex or another script should perform deeper
analysis.

## Watch for new posts

The watch command stores seen post IDs locally and only returns posts that are
new for the same watch definition.

```bash
python3 reddit-opencli/scripts/redditctl.py watch \
  --subreddit openai \
  --query "agents" \
  --limit 25 \
  --format md
```

Use a specific state file when you want a named watch:

```bash
python3 reddit-opencli/scripts/redditctl.py watch \
  --subreddit LocalLLaMA \
  --state-file ~/.local/state/kk-reddit/watch/local-llama.json \
  --format md
```

## Preview write actions

Write actions are public or account-affecting. The wrapper previews by default
and does not execute unless `--yes` is provided.

Preview a comment:

```bash
python3 reddit-opencli/scripts/redditctl.py act comment \
  "https://www.reddit.com/r/rust/comments/..." \
  --text "Thanks for sharing this. The tradeoff I would watch is build time."
```

Preview an upvote:

```bash
python3 reddit-opencli/scripts/redditctl.py act upvote \
  "https://www.reddit.com/r/rust/comments/..."
```

Preview save:

```bash
python3 reddit-opencli/scripts/redditctl.py act save \
  "https://www.reddit.com/r/rust/comments/..."
```

Preview subscribe:

```bash
python3 reddit-opencli/scripts/redditctl.py act subscribe rust
```

## Execute write actions after confirmation

Only add `--yes` after the user confirms the exact action and target.

```bash
python3 reddit-opencli/scripts/redditctl.py act comment \
  "https://www.reddit.com/r/rust/comments/..." \
  --text "Thanks for sharing this. The tradeoff I would watch is build time." \
  --yes
```

Other write actions:

```bash
python3 reddit-opencli/scripts/redditctl.py act upvote "<post-url-or-id>" --yes
python3 reddit-opencli/scripts/redditctl.py act downvote "<post-url-or-id>" --yes
python3 reddit-opencli/scripts/redditctl.py act unvote "<post-url-or-id>" --yes
python3 reddit-opencli/scripts/redditctl.py act save "<post-url-or-id>" --yes
python3 reddit-opencli/scripts/redditctl.py act unsave "<post-url-or-id>" --yes
python3 reddit-opencli/scripts/redditctl.py act subscribe rust --yes
python3 reddit-opencli/scripts/redditctl.py act unsubscribe rust --yes
```

## Direct opencli-rs commands

Use these when you need to bypass the wrapper:

```bash
opencli-rs reddit hot --subreddit rust --limit 20 -f json
opencli-rs reddit search "local llm" --limit 20 --sort relevance --time month -f json
opencli-rs reddit subreddit LocalLLaMA --sort top --time week --limit 20 -f json
opencli-rs reddit read "<post-url-or-id>" --limit 25 --depth 2 --sort best -f json
opencli-rs reddit comment <post-id> "comment text" -f json
opencli-rs reddit upvote <post-id> --direction up -f json
opencli-rs reddit save <post-id> -f json
opencli-rs reddit subscribe rust -f json
```
