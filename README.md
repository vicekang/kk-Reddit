# kk-Reddit

`kk-Reddit` is a Codex skill for Reddit workflows powered only by
OpenCLI (`opencli`).

It wraps `opencli reddit ...` with safer write handling, repeatable research
workflows, local watch state, and clear setup docs.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/vicekang/kk-Reddit/main/install.sh | bash
```

The installer will:

1. Install/check OpenCLI (`opencli`) with `npm install -g @jackwener/opencli`.
2. Copy the `reddit-opencli` skill into `${CODEX_HOME:-$HOME/.codex}/skills`.
3. Run `opencli doctor` to verify the browser bridge.

Restart or refresh Codex after installation so it discovers the skill.

## Requirements

- macOS or Linux shell.
- Node/npm for installing OpenCLI when it is missing.
- Chrome or Chromium.
- The OpenCLI Chrome extension connected to the local OpenCLI daemon.
- A Reddit login in Chrome for account-specific reads and all write actions.

Check setup:

```bash
opencli --version
opencli doctor
```

If the doctor output says the Chrome extension is missing or unstable, follow
[Chrome extension setup](docs/CHROME_EXTENSION.md).

## What It Does

- Research posts across subreddits, search queries, frontpage, and popular.
- Read posts and comments with limit, depth, sort, and Markdown/JSON output.
- Watch Reddit sources and show posts that are new since the last run.
- Preview and execute first-class write actions:
  comment, upvote, downvote, unvote, save, unsave, subscribe, unsubscribe.
- Require explicit confirmation before any write action executes.

## Use From Codex

Ask naturally:

- "Use reddit-opencli to find the top discussions about local LLMs in r/LocalLLaMA and r/selfhosted."
- "Read this Reddit thread and summarize the strongest objections."
- "Watch r/openai for new high-engagement posts about agents."
- "Prepare a Reddit comment for this post, show me the exact command, and wait before posting."
- "Subscribe me to r/rust after showing the action preview."

The skill uses the bundled wrapper:

```bash
python3 reddit-opencli/scripts/redditctl.py research --subreddit LocalLLaMA --query "agentic coding" --limit 20 --format md
python3 reddit-opencli/scripts/redditctl.py thread "https://www.reddit.com/r/rust/comments/..." --limit 20 --depth 2 --format md
python3 reddit-opencli/scripts/redditctl.py act upvote "https://www.reddit.com/r/rust/comments/..." --yes
```

For full command examples, see [Usage guide](docs/USAGE.md).

## Safety Model

Read-only commands can run directly. Write actions require a two-step flow:

1. Preview the target, text, risk, and exact `opencli reddit ...` command.
2. Execute only after the user explicitly confirms.

The wrapper will not execute a write action unless `--yes` is supplied.
Codex should only add `--yes` after the user confirms the exact action.

## Chrome Extension

The browser extension is named **OpenCLI**. It is the browser bridge used by
`opencli`; this project does not ship a separate Reddit-specific Chrome
extension in v1.

See [Chrome extension setup](docs/CHROME_EXTENSION.md) and
[extension notes](extension/README.md).

## Repository Layout

```text
kk-Reddit/
├── install.sh
├── reddit-opencli/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/reddit-opencli-reference.md
│   └── scripts/
│       ├── ensure_opencli.sh
│       └── redditctl.py
├── docs/
│   ├── CHROME_EXTENSION.md
│   └── USAGE.md
└── extension/
    └── README.md
```

## License

MIT

